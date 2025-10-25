from copy import deepcopy
import json
from typing import Any, Dict, List, Optional, Callable, Tuple
import logging
import openai
from openai import RateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .llm_history_manager import LLMHistoryManager
from .llm_token_utils import count_message_tokens
from .function_tools import autodiscover_tools

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
MAX_INPUT_TOKENS = 64000


class BuiltinToolsLLMClient:

    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        openai_client: openai.OpenAI = None,
        model: str = "qwen3-30b-a3b",
        stream_handler: Optional[Callable] = None,
        debug: bool = False,        
    ):
        self.client = openai_client or openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        
        self.stream_handler = stream_handler
        self.chat_history = LLMHistoryManager()
        self.debug = debug
        if self.debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

    def _execute_tool(
        self,
        tool: Callable,
        assistant_content: str,
        tool_call_id: str,
        tool_type: str,
        tool_name: str,
        tool_json_args: str,
        context: Optional[dict] = None,
    ) -> str:
        logger.info("_execute_tool %s - %s", tool_call_id, tool_name)
        
        tool_messages = [
            {
                        "id": tool_call_id,
                        "type": tool_type,
                        "function": {
                            "name": tool_name,
                            "arguments": tool_json_args,
                        },
            },
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": tool_name,
                "content": None,
            },
        ]
        try:
            tool_args  = json.loads(tool_json_args)            
            if context:
                tool_args["context"] = context

            result = tool(**tool_args)
        except Exception as e:
            result = f"Error executing tool {tool_name}: {str(e)}"

        if isinstance(result, list):
            tool_messages[-1]["content"] = result            
        else:
            tool_messages[-1]["content"] = json.dumps(result)        
        return tool_messages
    
    
    def _extend_history(self, messages: List[Dict[str, Any]], include_history: Optional[int] = None):        
        if include_history:           
            total_tokens = 0
            for msg in messages:
                # import json
                # print(">>>>>>>>>msg:", json.dumps(msg, indent=2))
                total_tokens += count_message_tokens(msg, model=self.model)                            
            hist_msgs = self.chat_history.get_chat_history(include_history)          
            req_msg = list(reversed(hist_msgs))
            fitted_msgs = []
            for msg in req_msg:
                msg_tokens = count_message_tokens(msg, model=self.model)
                if total_tokens + msg_tokens > MAX_INPUT_TOKENS:
                    break
                fitted_msgs.append(msg)
                total_tokens += msg_tokens
            fitted_msgs = list(reversed(fitted_msgs))                            
            return fitted_msgs  + messages      
        
        return messages
    
    
    
    def switch_model(self, model_id:str):        
        self.model = model_id    
    
    @retry(retry=retry_if_exception_type(RateLimitError), 
           stop=stop_after_attempt(3), 
           wait=wait_exponential(multiplier=1, min=4, max=10), 
           reraise=True)
    def invoke_chat_completions(self, **kwargs)->Any:
        response = self.client.chat.completions.create(                    
                    **kwargs,
                ) 
        return response
    
    
    def _handle_stream_response(self, response)->Tuple[str]:
        assistant_content = ""
        tool_calls = []
        tool_index = -1
        tool_call_id = None
        tool_type = None
        tool_name = None
        tool_args_json = ""
        is_tool_call = False
        for chunk in response:
            # print(chunk)
            delta = chunk.choices[0].delta if chunk.choices else None
            if not delta:
                continue
            # Text tokens
            if getattr(delta, "content", None):
                if self.stream_handler:
                    self.stream_handler(delta.content)
                assistant_content += delta.content
            # Tool call deltas            
            tcs = getattr(delta, "tool_calls", None)
            if tcs:
                if is_tool_call is False:
                    if self.stream_handler:
                        self.stream_handler("\n")
                    is_tool_call = True
                call = tcs[0]
                index = call.index  
                if call.id and call.function and index!=tool_index:                    
                    if tool_call_id and tool_name:
                        tool_calls.append((tool_call_id, tool_type, tool_name, tool_args_json)) 
                        tool_call_id = None
                        tool_name = None
                        tool_type = None
                        tool_args_json = "" 
                                        
                    tool_name = call.function.name                   
                    tool_call_id = call.id
                    tool_type = call.type
                    tool_args_json = call.function.arguments
                    tool_index = index
                    if self.stream_handler:
                        self.stream_handler(f"\ntool_name:{tool_name}\n")
                        self.stream_handler(f"tool_id:{tool_call_id}\n")
                elif call.function:
                    if self.stream_handler:
                        self.stream_handler(call.function.arguments)
                    tool_args_json += call.function.arguments
                    
            if chunk.choices[0].finish_reason == "tool_calls":
                if tool_call_id and tool_name:
                    tool_calls.append((tool_call_id, tool_type, tool_name, tool_args_json)) 
        if self.stream_handler:
            self.stream_handler("\n")   
        return assistant_content, tool_calls    
    
    
    def _handle_tool_calls(self, assistant_content, tool_calls, context, tools_mapping)->Tuple[str, List[Dict[str, Any]]]:
        calls = []
        results = []                   
        for tool_call_id, tool_type, tool_name, tool_args_json in tool_calls:  
            fuct, stateless = tools_mapping.get(tool_name)
            ctx = context if not stateless else None                
            tool_messages = self._execute_tool(
                fuct, assistant_content, tool_call_id, tool_type, tool_name, tool_args_json, ctx
            )   
            calls.append(tool_messages[0])
            results.append(tool_messages[1])                
        return calls, results
        

    def _invoke_model_with_params_adjustment(self, chat_params:Dict[str, Any], original_messages)->Any:
        response = None
        try:
            response = self.invoke_chat_completions(                           
                **chat_params,
            )
            for msg in original_messages:
                self.chat_history.add_entry(msg) 
        except openai.BadRequestError as e:            
            logger.error("messages:\n %s", json.dumps(chat_params["messages"], indent=2))
            logger.exception(e)            
            if "temperature" in chat_params:
                del chat_params["temperature"]
            if "tool_choice" in chat_params:    
                del chat_params["tool_choice"]
            try:
                response = self.invoke_chat_completions(                    
                    **chat_params,
                ) 
                for msg in original_messages:
                    self.chat_history.add_entry(msg) 
            except openai.BadRequestError as e:
                logger.error("messages:\n %s", json.dumps(chat_params["messages"], indent=2))
                logger.exception(e)
                raise e
        return response
    
    
    def _prepare_llm_params(
        self,
        model:str = None,
        inputs: Optional[List[dict]]= None,
        prompt: Optional[str] = None,
        tools: Optional[List[Callable]] = None,
        temperature: float = 0.1,
        reasoning_effort: Optional[str]  = None,
        system_prompt: Optional[str] = None,
        context: Optional[dict] = None,
        max_completion_tokens: Optional[int] = None,
        include_history: Optional[int] = None,
        stream:bool = False,
    ):
        
        assert inputs or prompt, 'either input or prompt is equired'        
        original_messages = deepcopy(inputs) if inputs else [{"role":"user", "content":prompt}]
        messages = deepcopy(original_messages)        
        if include_history:
            messages = self._extend_history(original_messages, include_history)        
        
        if system_prompt and messages and messages[0].get("role") != "system":
            messages.insert(0, {"role": "system", "content": system_prompt})

        
        tool_metas, tools_mapping = autodiscover_tools(tools) if tools else ([], {})
        chat_params = (
            {"tools": tool_metas} if tool_metas else {}
        )
        # "tool_choice": "auto",
        
        if reasoning_effort:
            chat_params["reasoning_effort"] = reasoning_effort
        
        if max_completion_tokens:
            chat_params["max_completion_tokens"] = max_completion_tokens
        
        temperature = 1 if self.model in ["gpt-5"] else temperature
        llm_model = model if model else self.model
        chat_params["temperature"]   = temperature  
        chat_params["messages"]   = messages   
        chat_params["stream"] = stream 
        chat_params["model"] = llm_model   
        return chat_params, original_messages, tools_mapping
        
    
    
    def invoke_chat_stream(
        self,
        model:str = None,
        inputs: Optional[List[dict]]= None,
        prompt: Optional[str] = None,
        tools: Optional[List[Callable]] = None,
        temperature: float = 0.1,
        reasoning_effort: Optional[str]  = None,
        system_prompt: Optional[str] = None,
        context: Optional[dict] = None,
        max_completion_tokens: Optional[int] = None,
        include_history: Optional[int] = None,
        
    ):
        chat_params, original_messages, tools_mapping = self._prepare_llm_params(
            model = model,
            inputs = inputs,
            prompt  = prompt,
            tools = tools,
            temperature = temperature,
            reasoning_effort = reasoning_effort,
            system_prompt = system_prompt,
            context = context,
            max_completion_tokens = max_completion_tokens,
            include_history = include_history,
            stream=True,
        )
        response = self._invoke_model_with_params_adjustment(chat_params, original_messages)
                    
        assistant_content , tool_calls = self._handle_stream_response(response) 
        
        if tool_calls:
            calls, results = self._handle_tool_calls(
                assistant_content, tool_calls, context, tools_mapping
            )
            assistant_msg = {"role":"assistant", "content":assistant_content, "tool_calls": calls}                       
            chat_params["messages"] = [assistant_msg]
            chat_params["messages"].extend(results)
            return self.invoke_chat_stream(                  
                    model = model,
                    inputs = chat_params["messages"],
                    prompt  = prompt,
                    tools = tools,
                    temperature = temperature,
                    reasoning_effort = reasoning_effort,
                    system_prompt = system_prompt,
                    context = context,
                    max_completion_tokens = max_completion_tokens,
                    include_history = include_history                 
                ) 
        
        self.chat_history.add_entry({"role":"assistant", "content":assistant_content})
        return assistant_content
    
      
    
    def invoke_chat(
        self,
        model:str = None,
        inputs: Optional[List[dict]]= None,
        prompt: Optional[str] = None,
        tools: Optional[List[Callable]] = None,
        temperature: float = 0.1,
        reasoning_effort: Optional[str]  = None,
        system_prompt: Optional[str] = None,
        context: Optional[dict] = None,
        max_completion_tokens: Optional[int] = None,
        include_history: Optional[int] = None,
    ):
        chat_params, original_messages, tools_mapping = self._prepare_llm_params(
            model = model,
            inputs = inputs,
            prompt  = prompt,
            tools = tools,
            temperature = temperature,
            reasoning_effort = reasoning_effort,
            system_prompt = system_prompt,
            context = context,
            max_completion_tokens = max_completion_tokens,
            include_history = include_history,
            stream=False,
        )
        response = self._invoke_model_with_params_adjustment(chat_params, original_messages)       
        try:
            tool_calls = []        
            tool_call_id = None
            tool_name = None
            tool_type = None
            tool_args_json = ""
            logger.info("Response:", response.choices[0].finish_reason)        
            if response.choices[0].finish_reason == "stop":
                assistant_content = response.choices[0].message.content  
            
            tcs = getattr(response.choices[0].message, "tool_calls") or []
            for call in tcs:
                tool_call_id = call.id
                tool_type = call.type
                tool_name = call.function.name
                tool_args_json = call.function.arguments
                tool_calls.append((tool_call_id, tool_type, tool_name, tool_args_json))
                
            if tool_calls:  
                calls, results = self._handle_tool_calls(
                    assistant_content, tool_calls, context, tools_mapping
                )
                assistant_msg = {"role":"assistant", "content":assistant_content, "tool_calls": calls}                       
                chat_params["messages"] = [assistant_msg]
                chat_params["messages"].extend(results)
                return self.invoke_chat(                
                                model = model,
                                inputs = inputs,
                                prompt  = prompt,
                                tools = tools,
                                temperature = temperature,
                                reasoning_effort = reasoning_effort,
                                system_prompt = system_prompt,
                                context = context,
                                max_completion_tokens = max_completion_tokens,
                                include_history = include_history,                               
                            ) 
            self.chat_history.add_entry({"role":"assistant", "content":assistant_content})
        except Exception as err:
            logger.exception(err)
            
        return assistant_content