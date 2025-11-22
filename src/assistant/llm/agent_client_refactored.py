"""
Refactored Agent Client implementing Python best practices and OOP design principles.

This module provides a refactored implementation of the LLM agent client with:
- Proper separation of concerns
- Single responsibility principle
- Improved error handling
- Comprehensive type hints and documentation
"""

import json
import logging
import re
from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import openai
from openai import RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from assistant.config.manager import AssistantConfig
from assistant.agents.agent_discovery import discover_tools
from ..utils.llm.error_logger import log_error
from ..utils.llm.token_utils import count_message_tokens
from .client import LLMClient
from .history import LLMChatHistoryManager


logger = logging.getLogger(__name__)
MAX_INPUT_TOKENS = 64000


class ToolExecutionHandler:
    """Handles tool execution with proper error handling and result formatting."""
    
    def __init__(self, stream_handler: Optional[Callable] = None):
        self.stream_handler = stream_handler
    
    def execute_tool(
        self,
        tool: Callable,
        assistant_content: str,
        tool_call_id: str,
        tool_type: str,
        tool_name: str,
        tool_json_args: str,
        context: Optional[dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a tool with proper error handling and result formatting.
        
        Args:
            tool: The callable tool to execute
            assistant_content: Content from the assistant response  
            tool_call_id: Unique identifier for the tool call
            tool_type: Type of tool being called
            tool_name: Name of the tool being executed
            tool_json_args: JSON string containing tool arguments
            context: Optional context dictionary for stateful tools
            
        Returns:
            List of message dictionaries representing the tool execution result
        """
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
            tool_args = json.loads(tool_json_args)
            if context:
                tool_args["context"] = context

            result = tool(**tool_args)
        except Exception as e:
            result = f"Error executing tool {tool_name}: {str(e)}"
            
        # Format the result properly
        if isinstance(result, list):
            tool_messages[-1]["content"] = result
        else:
            tool_messages[-1]["content"] = json.dumps(result)
            
        print(f"\nTool {tool_name} execution completed:")
        return tool_messages


class ParameterAdjuster:
    """Handles parameter adjustment for LLM calls based on various error conditions."""
    
    @staticmethod
    def adjust_parameters_for_bad_request(
        chat_params: Dict[str, Any], 
        original_messages: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Adjust parameters when a bad request occurs.
        
        Args:
            chat_params: Current chat parameters
            original_messages: Original messages for history tracking
            
        Returns:
            Tuple of adjusted parameters and whether adjustment was made
        """
        # This would be implemented based on specific error handling needs
        return chat_params, False
    
    @staticmethod
    def adjust_parameters_for_token_limit(
        chat_params: Dict[str, Any],
        original_messages: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Adjust parameters when token limit is exceeded.
        
        Args:
            chat_params: Current chat parameters  
            original_messages: Original messages for history tracking
            
        Returns:
            Tuple of adjusted parameters and whether adjustment was made
        """
        # This would be implemented based on specific error handling needs
        return chat_params, False


class AgentOrchestrator(LLMClient):
    """Refactored LLM agent orchestrator implementing proper OOP design principles."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        openai_client: Optional[openai.OpenAI] = None,
        stream_handler: Optional[Callable] = None,
        debug: bool = False,
        config: Optional[AssistantConfig] = None,
    ):
        """
        Initialize the Agent Orchestrator.
        
        Args:
            base_url: Base URL for LLM API
            api_key: API key for authentication  
            openai_client: Pre-configured OpenAI client
            stream_handler: Handler function for streaming responses
            debug: Enable debug logging
            config: Assistant configuration object
        """
        super().__init__(config)
        self.client = openai_client or self._get_llm()
        if base_url:
            self.client.base_url = base_url
        if api_key:
            self.client.api_key = api_key

        self.model = self.llm_models[0]
        self.stream_handler = stream_handler
        
        hist_file = config.get_option("llm", "chat_history_file", None) if config else None
        self.chat_history = LLMChatHistoryManager(history_file_path=hist_file)
        self.debug = debug
        if self.debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
            
        # Initialize components
        self.tool_handler = ToolExecutionHandler(stream_handler)

    def _extend_history(
        self, 
        messages: List[Dict[str, Any]], 
        include_history: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Extend messages with chat history up to the specified limit.
        
        Args:
            messages: Current message list
            include_history: Number of historical messages to include
            
        Returns:
            Extended message list with history included
        """
        if include_history:
            total_tokens = 0
            for msg in messages:
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
            return fitted_msgs + messages

        return messages

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def invoke_chat_completions(self, **kwargs) -> Any:
        """
        Invoke chat completions with rate limiting retry logic.
        
        Args:
            **kwargs: Chat completion parameters
            
        Returns:
            Response from the LLM
        """
        # Extract and process messages for parameter adjustment
        start_index = 0
        end_index = 0
        
        if "messages" in kwargs and kwargs["messages"]:
            if kwargs["messages"][0].get("role") == "system":
                start_index = 1
                
            for i in range(start_index, len(kwargs["messages"])):
                msg = kwargs["messages"][i]
                if msg.get("role") != "tool":
                    end_index = i
                    break

        params = {**kwargs}
        if end_index > start_index:
            params["messages"] = (
                kwargs["messages"][0:start_index] + kwargs["messages"][end_index:]
            )

        has_mcp = any([tool.get("type") == "mcp" for tool in params.get("tools", [])])
        if has_mcp:
            response = self.invoke_responses(**params)
        else:
            response = self.client.chat.completions.create(**params)
            
        return response

    @retry(
        retry=retry_if_exception_type(RateLimitError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def invoke_responses(self, **kwargs) -> Any:
        """
        Invoke responses with rate limiting retry logic.
        
        Args:
            **kwargs: Response parameters
            
        Returns:
            Response from the LLM
        """
        # Extract and process messages for parameter adjustment  
        start_index = 0
        end_index = 0
        
        if "messages" in kwargs and kwargs["messages"]:
            if kwargs["messages"][0].get("role") == "system":
                start_index = 1
                
            for i in range(start_index, len(kwargs["messages"])):
                msg = kwargs["messages"][i]
                if msg.get("role") != "tool":
                    end_index = i
                    break

        params = {**kwargs}
        if end_index > start_index:
            params["messages"] = (
                kwargs["messages"][0:start_index] + kwargs["messages"][end_index:]
            )

        response = self.client.responses.create(**params)
        return response

    def _handle_stream_response(self, response) -> Tuple[str, List[Tuple]]:
        """
        Handle streaming responses from the LLM.
        
        Args:
            response: Streaming response object
            
        Returns:
            Tuple of assistant content and tool calls
        """
        assistant_content = ""
        tool_calls = []
        tool_index = -1
        tool_call_id = None
        tool_type = None
        tool_name = None
        tool_args_json = ""
        is_tool_call = False
        
        for chunk in response:
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
                
                if call.id and call.function and index != tool_index:
                    if tool_call_id and tool_name:
                        tool_calls.append(
                            (tool_call_id, tool_type, tool_name, tool_args_json)
                        )
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
                    tool_calls.append(
                        (tool_call_id, tool_type, tool_name, tool_args_json)
                    )
                    
        if self.stream_handler:
            self.stream_handler("\n")
            
        return assistant_content, tool_calls

    def _handle_tool_calls(
        self,
        assistant_content: str,
        tool_calls: List[Tuple],
        context: Optional[dict],
        tools_mapping: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Handle execution of tool calls.
        
        Args:
            assistant_content: Content from the assistant response
            tool_calls: List of tool call tuples  
            context: Context for tool execution
            tools_mapping: Mapping of tool names to functions
            
        Returns:
            Tuple of calls and results lists
        """
        calls = []
        results = []
        
        for tool_call_id, tool_type, tool_name, tool_args_json in tool_calls:
            if tool_name in tools_mapping:
                fuct, stateless = tools_mapping.get(tool_name)
                ctx = context if not stateless else None
                
                tool_messages = self.tool_handler.execute_tool(
                    fuct,
                    assistant_content,
                    tool_call_id,
                    tool_type,
                    tool_name,
                    tool_args_json,
                    ctx,
                )
                
                calls.append(tool_messages[0])
                results.append(tool_messages[1])
            else:
                print(
                    "No Agent found for tool:",
                    tool_call_id,
                    tool_type,
                    tool_name,
                    json.dumps(tool_args_json, indent=2),
                )
                
        return calls, results

    def _clean_tool_calls_from_messages(
        self, messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove tool call related messages from the message list.
        
        Args:
            messages: Message list to clean
            
        Returns:
            Cleaned message list
        """
        cleaned_msgs = []
        for msg in messages:
            if msg.get("role") != "tool" and "tool_calls" not in msg:
                cleaned_msgs.append(msg)
                
        return cleaned_msgs

    def _reduce_input_messages(
        self, messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Reduce input messages when token limit is exceeded.
        
        Args:
            messages: Input message list
            
        Returns:
            Reduced message list
        """
        has_sys_msg = messages[0].get("role") == "system"
        cleaned_msgs = []
        
        if has_sys_msg:
            cleaned_msgs.append(messages[0])
            messages = messages[1:]

        if len(messages) == 1:
            raise ValueError("input text exceeded input token limit")

        hindex = int(len(messages) / 2)
        for x in range(hindex):
            index = hindex - x
            msg = messages[index]
            if msg.get("role") in ["user", "assistant"]:
                hindex = index
                break

        cleaned_msgs.extend(messages[hindex:])
        return cleaned_msgs

    def _invoke_model_with_params_adjustment(
        self, 
        chat_params: Dict[str, Any], 
        original_messages: List[Dict[str, Any]]
    ) -> Any:
        """
        Invoke model with parameter adjustment for various error conditions.
        
        Args:
            chat_params: Chat parameters to use
            original_messages: Original messages for history tracking
            
        Returns:
            Response from the LLM
        """
        response = None
        
        try:
            response = self.invoke_chat_completions(**chat_params)
            
            # Add all original messages to chat history
            for msg in original_messages:
                self.chat_history.add_entry(msg)
                
        except openai.BadRequestError as e:
            if "does not support parameters: ['tools']" in str(e):
                logger.warning(
                    "LLM model does not support tools, retrying without tools..."
                )
                print("LLM model does not support tools, retrying without tools...")
                
                if "tools" in chat_params:
                    del chat_params["tools"]
                    
                if "tool_choice" in chat_params:
                    del chat_params["tool_choice"]
                    
                chat_params["messages"] = self._clean_tool_calls_from_messages(
                    chat_params["messages"]
                )

            elif "The maximum tokens you requested exceeds the model limit of" in str(e):
                logger.warning(
                    "LLM model max tokens exceeded, adjusting max_completion_tokens and retrying..."
                )
                
                match = re.search(r"exceeds the model limit of (\d+)", str(e))
                if match:
                    model_limit = int(match.group(1))
                    logger.info(f"Model limit extracted: {model_limit}")
                    
                    # Adjust max_completion_tokens based on model limit
                    chat_params["max_completion_tokens"] = model_limit
                    logger.info(f"Adjusted max_completion_tokens to {model_limit}")
                else:
                    logger.error("Could not extract model limit from error message.")
                    
            elif "Input is too long for requested model" in str(e):
                logger.warning(
                    "input token exceeded, adjusting input message and retrying..."
                )
                
                chat_params["messages"] = self._reduce_input_messages(
                    chat_params["messages"]
                )

            elif "Only temperature=1 is supported" in str(e):
                logger.warning(
                    "LLM model only supports temperature=1, adjusting and retrying..."
                )
                chat_params["temperature"] = 1
                
            else:
                log_error(str(e), **chat_params)
                raise e
                
            return self._invoke_model_with_params_adjustment(
                chat_params, original_messages
            )
            
        except TypeError as e:
            match = re.search(r"got an unexpected keyword argument '(\w+)'", str(e))
            if match:
                unexpected_arg = match.group(1)
                logger.warning(
                    f"LLM client does not support parameter: {unexpected_arg}, retrying without it..."
                )
                
                if unexpected_arg in chat_params:
                    del chat_params[unexpected_arg]
                    
            else:
                log_error(str(e), **chat_params)
                raise e
                
            return self._invoke_model_with_params_adjustment(
                chat_params, original_messages
            )
            
        return response

    def _prepare_llm_call_params(
        self,
        model: Optional[str] = None,
        inputs: Optional[List[dict]] = None,
        prompt: Optional[str] = None,
        tools: Optional[List[Callable]] = None,
        temperature: float = 0.1,
        reasoning_effort: Optional[str] = None,
        system_prompt: Optional[str] = None,
        context: Optional[dict] = None,
        max_completion_tokens: Optional[int] = None,
        include_history: Optional[int] = None,
        stream: bool = False,
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Prepare parameters for LLM call.
        
        Args:
            model: LLM model to use
            inputs: Input messages  
            prompt: Prompt string
            tools: List of callable tools
            temperature: Sampling temperature
            reasoning_effort: Reasoning effort level
            system_prompt: System prompt content
            context: Context for tool execution
            max_completion_tokens: Maximum completion tokens
            include_history: Number of history items to include
            stream: Whether to use streaming
            
        Returns:
            Tuple of chat_params, original_messages, and tools_mapping
        """
        assert inputs or prompt, "either input or prompt is required"
        
        original_messages = (
            deepcopy(inputs) if inputs else [{"role": "user", "content": prompt}]
        )
        
        messages = deepcopy(original_messages)
        
        if include_history:
            messages = self._extend_history(original_messages, include_history)

        if system_prompt and messages and messages[0].get("role") != "system":
            messages.insert(0, {"role": "system", "content": system_prompt})

        tool_metas, tools_mapping = discover_tools(tools) if tools else ([], {})
        
        # Prepare tools metadata
        tools_metadata = []
        tools_metadata.extend(tool_metas)
        
        chat_params = {"tools": tools_metadata} if tools_metadata else {}
        
        if reasoning_effort:
            chat_params["reasoning_effort"] = reasoning_effort

        if max_completion_tokens:
            chat_params["max_completion_tokens"] = max_completion_tokens

        temperature = 1 if self.model in ["gpt-5"] else temperature
        llm_model = model if model else self.model
        
        chat_params["temperature"] = temperature
        chat_params["messages"] = messages
        chat_params["stream"] = stream
        chat_params["model"] = llm_model
        
        return chat_params, original_messages, tools_mapping

    def invoke_chat_stream(
        self,
        model: Optional[str] = None,
        inputs: Optional[List[dict]] = None,
        prompt: Optional[str] = None,
        tools: Optional[List[Callable]] = None,
        temperature: float = 0.1,
        reasoning_effort: Optional[str] = None,
        system_prompt: Optional[str] = None,
        context: Optional[dict] = None,
        max_completion_tokens: Optional[int] = None,
        include_history: Optional[int] = None,
    ) -> Union[str, List[Dict[str, Any]]]:
        """
        Invoke chat with streaming response.
        
        Args:
            model: LLM model to use
            inputs: Input messages  
            prompt: Prompt string
            tools: List of callable tools
            temperature: Sampling temperature
            reasoning_effort: Reasoning effort level
            system_prompt: System prompt content
            context: Context for tool execution
            max_completion_tokens: Maximum completion tokens
            include_history: Number of history items to include
            
        Returns:
            Streaming response or list of messages
        """
        chat_params, original_messages, tools_mapping = self._prepare_llm_call_params(
            model=model,
            inputs=inputs,
            prompt=prompt,
            tools=tools,
            temperature=temperature,
            reasoning_effort=reasoning_effort,
            system_prompt=system_prompt,
            context=context,
            max_completion_tokens=max_completion_tokens,
            include_history=include_history,
            stream=True,
        )
        
        response = self._invoke_model_with_params_adjustment(
            chat_params, original_messages
        )

        assistant_content, tool_calls = self._handle_stream_response(response)

        if tool_calls:
            calls, results = self._handle_tool_calls(
                assistant_content, tool_calls, context, tools_mapping
            )
            
            assistant_msg = {
                "role": "assistant",
                "content": assistant_content,
                "tool_calls": calls,
            }
            
            chat_params["messages"] = [assistant_msg]
            chat_params["messages"].extend(results)
            
            return self.invoke_chat_stream(
                model=model,
                inputs=chat_params["messages"],
                prompt=prompt,
                tools=tools,
                temperature=temperature,
                reasoning_effort=reasoning_effort,
                system_prompt=system_prompt,
                context=context,
                max_completion_tokens=max_completion_tokens,
                include_history=include_history,
            )

        self.chat_history.add_entry({"role": "assistant", "content": assistant_content})
        return assistant_content

    def invoke_chat(
        self,
        model: Optional[str] = None,
        inputs: Optional[List[dict]] = None,
        prompt: Optional[str] = None,
        tools: Optional[List[Callable]] = None,
        temperature: float = 0.1,
        reasoning_effort: Optional[str] = None,
        system_prompt: Optional[str] = None,
        context: Optional[dict] = None,
        max_completion_tokens: Optional[int] = None,
        include_history: Optional[int] = None,
    ) -> Union[str, List[Dict[str, Any]]]:
        """
        Invoke chat with non-streaming response.
        
        Args:
            model: LLM model to use
            inputs: Input messages  
            prompt: Prompt string
            tools: List of callable tools
            temperature: Sampling temperature
            reasoning_effort: Reasoning effort level
            system_prompt: System prompt content
            context: Context for tool execution
            max_completion_tokens: Maximum completion tokens
            include_history: Number of history items to include
            
        Returns:
            Response string or list of messages
        """
        chat_params, original_messages, tools_mapping = self._prepare_llm_call_params(
            model=model,
            inputs=inputs,
            prompt=prompt,
            tools=tools,
            temperature=temperature,
            reasoning_effort=reasoning_effort,
            system_prompt=system_prompt,
            context=context,
            max_completion_tokens=max_completion_tokens,
            include_history=include_history,
            stream=False,
        )
        
        response = self._invoke_model_with_params_adjustment(
            chat_params, original_messages
        )
        
        try:
            tool_calls = []
            tool_call_id = None
            tool_name = None
            tool_type = None
            tool_args_json = ""
            
            logger.info("Response: %s", response.choices[0].finish_reason)
            
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
                
                assistant_msg = {
                    "role": "assistant",
                    "content": assistant_content,
                    "tool_calls": calls,
                }
                
                chat_params["messages"] = [assistant_msg]
                chat_params["messages"].extend(results)
                
                return self.invoke_chat(
                    model=model,
                    inputs=inputs,
                    prompt=prompt,
                    tools=tools,
                    temperature=temperature,
                    reasoning_effort=reasoning_effort,
                    system_prompt=system_prompt,
                    context=context,
                    max_completion_tokens=max_completion_tokens,
                    include_history=include_history,
                )
                
            self.chat_history.add_entry(
                {"role": "assistant", "content": assistant_content}
            )
            
        except Exception as err:
            logger.exception(err)

        return assistant_content