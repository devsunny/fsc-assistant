"""LLM client facade that composes the new runtime collaborators."""
from __future__ import annotations

import json
import logging
from typing import Iterable, Optional

from openai import BadRequestError, OpenAIError, RateLimitError

from assistant.config.manager import AssistantConfig
from assistant.llm.runtime import (
    ChatRequest,
    LLMConfigurationAdapter,
    LLMRuntime,
    LLMTransportClient,
    create_llm_runtime,
)

logger = logging.getLogger(__name__)


class LLMClient:
    """Backward compatible facade exposing simple completion helpers."""

    def __init__(self, config: Optional[AssistantConfig] = None):
        self._config_adapter = LLMConfigurationAdapter(config)
        self._runtime: LLMRuntime = create_llm_runtime(config_adapter=self._config_adapter)
        self.config = self._runtime.config_adapter.assistant_config
        self.provider_config = self._runtime.provider_config
        self.llm_models = self.provider_config.models
        self.max_completion_tokens = self.provider_config.max_completion_tokens
        self.user_selected_model: Optional[str] = None

    @property
    def transport(self) -> LLMTransportClient:
        return self._runtime.transport

    @property
    def native_client(self):
        return self.transport.client

    def get_timeout(self):
        return self.provider_config.timeout.as_httpx_timeout()

    def invoke_model(
        self,
        prompt=None,
        messages=None,
        max_tokens: int = 0,
        max_completion_tokens: int = 0,
    ) -> Optional[str]:
        input_messages = (
            messages if messages is not None else [{"role": "user", "content": prompt}]
        )
        req_max_tokens = max(max_tokens, max_completion_tokens) or None
        if req_max_tokens and req_max_tokens > self.max_completion_tokens:
            req_max_tokens = self.max_completion_tokens

        for model_id in self._candidate_models():
            request = ChatRequest(
                messages=input_messages,
                model=model_id,
                max_completion_tokens=req_max_tokens,
            )
            try:
                response = self.transport.execute_chat(request).raw
                return response.choices[0].message.content
            except RateLimitError as err:
                logger.error("Rate limit exceeded: %s", err)
            except BadRequestError as err:
                logger.error("Bad request error: %s", err)
            except OpenAIError as err:
                logger.error("OpenAI error: %s", err)
            except Exception as err:  # pylint: disable=broad-except
                logger.error("Unexpected error invoking model: %s", err)

        return None

    def invoke_model_stream(
        self,
        prompt=None,
        messages=None,
        max_tokens: int = 0,
        max_completion_tokens: int = 0,
        temperature=0.1,
    ) -> Iterable[str]:
        yield from self.invoke_model_generator(
            prompt=prompt,
            messages=messages,
            max_tokens=max_tokens,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
        )

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
        max_completion_tokens: int = 16_000,
        temperature=0.1,
        system_prompt=None,
        model_id: Optional[str] = None,
    ):
        assert prompt is not None or messages is not None, "prompt or messages is required"
        input_messages = (
            messages if messages is not None else [{"role": "user", "content": prompt}]
        )
        if system_prompt:
            input_messages = [{"role": "system", "content": system_prompt}] + input_messages

        req_max_tokens = max(max_tokens, max_completion_tokens, self.max_completion_tokens)
        if req_max_tokens and req_max_tokens > self.max_completion_tokens:
            req_max_tokens = self.max_completion_tokens

        logger.debug("Messages to LLM: %s", json.dumps(input_messages, indent=2))

        models = [model_id] if model_id else list(self._candidate_models())
        for candidate in models:
            logger.debug("Running against model: %s", candidate)
            request = ChatRequest(
                messages=input_messages,
                model=candidate,
                temperature=temperature,
                max_completion_tokens=req_max_tokens,
            )
            try:
                stream = self.transport.stream_chat(request)
                response_text = ""
                for chunk in stream:
                    delta = chunk.raw.choices[0].delta
                    resp_chunk = getattr(delta, "content", None)
                    if resp_chunk is not None:
                        response_text += resp_chunk
                        yield resp_chunk
                if response_text:
                    break
            except RateLimitError as err:
                logger.error("Rate limit exceeded: %s", err)
            except BadRequestError as err:
                logger.error("Bad request error: %s", err)
            except OpenAIError as err:
                logger.error("OpenAI error: %s", err)
            except Exception as err:  # pylint: disable=broad-except
                logger.error("Unexpected error invoking model stream: %s", err)

    def _candidate_models(self) -> Iterable[str]:
        preferred = self.user_selected_model
        return self.transport.available_models(preferred)


llmclient = LLMClient()


if __name__ == "__main__":
    for chunk in llmclient.invoke_model_stream("write a 100 words story"):
        print(chunk, end="", flush=True)
