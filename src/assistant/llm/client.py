import getpass
import json
import logging
from typing import Optional

import httpx
from openai import BadRequestError, OpenAI, OpenAIError, RateLimitError

from ..config.manager import AssistantConfig

logger = logging.getLogger(__name__)


KEY_BASE_URL = "base_url"
KEY_API_KEY = "api_key"
KEY_CLIENT_ID = "client_id"
KEY_CLIENT_SECRET = "client_secret"
KEY_MAX_COMPLETION_TOKENS = "max_completion_tokens"
KEY_LLM = "llm"
KEY_MODELS = "models"
KEY_PROVIDER = "provider"


class LLMClient:

    def __init__(self, config: AssistantConfig = None):
        self.config = config if config is not None else AssistantConfig()
        self.llm_provider = self.config.get_option(
            KEY_LLM, KEY_PROVIDER, default="default"
        )
        if self.llm_provider == "default":
            llm_key = KEY_LLM
        else:
            llm_key = self.llm_provider

        self.base_url = self.config.get_option(llm_key, KEY_BASE_URL)
        self.api_key = self.config.get_option(llm_key, KEY_API_KEY)
        self.client_id = self.config.get_option(llm_key, KEY_CLIENT_ID)
        self.client_secret = self.config.get_option(llm_key, KEY_CLIENT_SECRET)
        self.max_completion_tokens = self.config.get_int(
            llm_key, KEY_MAX_COMPLETION_TOKENS, default=150000
        )
        self.user_selected_model = None
        models = self.config.get_option(llm_key, KEY_MODELS)
        assert (
            models is not None and len(models) > 0
        ), f"please config LLM models in {AssistantConfig.CONFIG_FILENAME}"
        self.llm_models = [models] if isinstance(models, str) else models
        if self.llm_provider != "openai":
            assert (
                self.base_url is not None
            ), f"please config LLM base url in {AssistantConfig.CONFIG_FILENAME}"
            if self.api_key is None:
                assert (
                    self.client_id is not None
                ), f"please config LLM client_id in {AssistantConfig.CONFIG_FILENAME}"
                assert (
                    self.client_secret is not None
                ), f"please config LLM client_secret in {AssistantConfig.CONFIG_FILENAME}"
        elif self.llm_provider == "openai":
            assert (
                self.api_key is not None
            ), f"please config LLM api_key in {AssistantConfig.CONFIG_FILENAME}"
        self.granular_timeout = self.get_timeout()

    @property
    def native_client(self):
        return self._get_llm()

    def get_timeout(self) -> httpx.Timeout:
        read_timeout = self.config.get_float("llm", "read_timeout", default=180)
        connect_timeout = self.config.get_float("llm", "connect_timeout", default=5.0)
        write_timeout = self.config.get_float("llm", "write_timeout", default=5.0)
        granular_timeout = httpx.Timeout(
            read_timeout,
            connect=connect_timeout,
            read=read_timeout,
            write=write_timeout,
        )
        return granular_timeout

    def _get_llm(self) -> OpenAI:
        extra_headers = None
        if self.client_id and self.client_secret:
            extra_headers = {
                "Client-Id": self.client_id,
                "Client-Secret": self.client_secret,
                "Application-Name": "Atlas-Phanes",
                "Username": getpass.getuser(),
            }

        llm = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.granular_timeout,
            default_headers=extra_headers,
        )
        return llm

    def invoke_model(
        self,
        prompt=None,
        messages=None,
        max_tokens: int = 0,
        max_completion_tokens: int = 0,
    ) -> str:
        llm = self._get_llm()
        req_max_tokens = max(max_tokens, max_completion_tokens)
        if req_max_tokens == 0:
            req_max_tokens = None

        if req_max_tokens and req_max_tokens > self.max_completion_tokens:
            req_max_tokens = self.max_completion_tokens

        input_messages = (
            messages if messages is not None else [{"role": "user", "content": prompt}]
        )

        for model_id in self.llm_models:
            try:

                response = llm.chat.completions.create(
                    model=model_id,  # or any other model you want to use
                    max_tokens=req_max_tokens,
                    messages=input_messages,
                )
                return response.choices[0].message.content
            except RateLimitError as e:
                logger.error(f"Rate limit exceeded: {e}")
                # Implement retry logic or backoff strategy here
            except BadRequestError as e:
                logger.error(f"Bad request error: {e.message}")
            except OpenAIError as e:
                logger.error(f"An OpenAI API error occurred: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")

        return None

    def invoke_model_stream(
        self,
        prompt=None,
        messages=None,
        max_tokens: int = 0,
        max_completion_tokens: int = 0,
        temperature=0.1,
    ):
        for chunk in self.invoke_model_generator(
            prompt=prompt,
            messages=messages,
            max_tokens=max_tokens,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
        ):
            yield chunk

    def invoke_model_stream_with_return(
        self,
        prompt=None,
        messages=None,
        max_tokens: int = 0,
        max_completion_tokens: int = 0,
        temperature=0.1,
    ) -> str:
        resp_text = ""
        for chunk in self.invoke_model_generator(
            prompt=prompt,
            messages=messages,
            max_tokens=max_tokens,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
        ):
            print(chunk, end="", flush=True)
            resp_text += chunk
        return resp_text

    def invoke_model_generator(
        self,
        prompt=None,
        messages=None,
        max_tokens: int = 0,
        max_completion_tokens: int = 16000,
        temperature=0.1,
        system_prompt=None,
        model_id: Optional[str] = None,
    ):
        assert (
            prompt is not None or messages is not None
        ), "prompt or messages is required"
        llm = self._get_llm()
        req_max_tokens = max(
            max_tokens, max_completion_tokens, self.max_completion_tokens
        )

        if req_max_tokens and req_max_tokens > self.max_completion_tokens:
            req_max_tokens = self.max_completion_tokens

        logging.info(f"max_completion_tokens = {req_max_tokens}")
        input_messages = (
            messages if messages is not None else [{"role": "user", "content": prompt}]
        )
        if system_prompt:
            input_messages.insert(0, {"role": "system", "content": system_prompt})

        if model_id is not None:
            models = [model_id]
        else:
            models = self.llm_models

        logger.debug(f"Messages to LLM: {json.dumps(input_messages, indent=2)}")

        for model_id in models:
            logger.debug(f"Ruuning against model:{model_id}")
            response_txt = ""
            try:
                stream = llm.chat.completions.create(
                    model=model_id,  # or any other model you want to use
                    max_tokens=req_max_tokens,
                    messages=input_messages,
                    stream=True,
                )
                for chunk in stream:
                    finish_reason = chunk.choices[0].finish_reason
                    resp_chunk = chunk.choices[0].delta.content
                    if resp_chunk is not None:
                        response_txt += resp_chunk
                        yield resp_chunk

                if response_txt:
                    break
            except RateLimitError as e:
                logger.error(f"Rate limit exceeded: {e}")
                # Implement retry logic or backoff strategy here
            except BadRequestError as e:
                logger.error(f"Bad request error: {e.message}")
            except OpenAIError as e:
                logger.error(f"An OpenAI API error occurred: {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")

        return None


llmclient = LLMClient()


if __name__ == "__main__":
    for chunk in llmclient.invoke_model_stream("write a 100 words story"):
        print(chunk, end="", flush=True)
