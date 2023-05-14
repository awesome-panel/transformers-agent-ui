"""Provides the TransformersAgent

A wrapper of the Hugging Face transformers agent. See
https://huggingface.co/docs/transformers/transformers_agents
"""
import logging
from datetime import datetime

import param
from transformers import HfAgent, OpenAiAgent

from transformers_agent_ui.domain.config import AGENT_CONFIGURATION
from transformers_agent_ui.domain.store import Store
from transformers_agent_ui.domain.token import TokenManager
from transformers_agent_ui.domain.run_input import RunInput

log = logging.getLogger(__name__)


def _get_agent(agent, model, token):
    """Returns the agent"""
    # pylint: disable=line-too-long
    params = AGENT_CONFIGURATION[agent]["models"][model]
    if agent == "HuggingFace":
        return HfAgent(
            **params,
            token=token,
        )
    if agent == "OpenAI":
        return OpenAiAgent(
            **params,
            api_key=token,
        )

    raise ValueError(f"The agent {agent} and model {model} is not supported")


class TransformersAgent(RunInput, param.Parameterized):
    """A wrapper of the Hugging Face transformers agent. See
    https://huggingface.co/docs/transformers/transformers_agents"""

    result = param.Parameter(precedence=-1)
    remote = param.Boolean(default=True, readonly=True)

    is_running = param.Boolean()

    use_cache: bool = param.Boolean(
        default=True, doc="If True a Cache is used to speed up run and to bring the the costs."
    )
    cache: Store = param.ClassSelector(class_=Store, precedence=-1)
    token_manager: TokenManager = param.ClassSelector(class_=TokenManager, precedence=-1)

    def __init__(self, **params):
        if "cache" not in params:
            params["cache"] = Store()
        if "token_manager" not in params:
            params["token_manager"] = TokenManager()
        super().__init__(**params)

    def get_token(self) -> str:
        """Returns the token"""
        return self.token_manager.get(self.agent)

    def get_agent(self, token: str):
        """Returns the Agent"""
        return _get_agent(agent=self.agent, model=self.model, token=token)

    def run(self):
        """Runs the agent, model on the `value`"""
        exception_raised = False
        self.is_running = True
        if self.use_cache and self.cache.exists(
            agent=self.agent, model=self.model, query=self.task
        ):
            result = self.cache.read(agent=self.agent, model=self.model, query=self.task)
            print(
                f"{datetime.now()} Cache hit for agent='{self.agent}', model='{self.model}' "
                f"and query='{self.task}'"
            )
        else:
            token = self.get_token()
            if not token:
                self._handle_no_token(self.agent)
                result = None
                exception_raised = True
            else:
                agent = self.get_agent(token=token)
                if self.kwargs:
                    kwargs = self.kwargs.copy()
                else:
                    kwargs = {}
                if self.result and "output" not in kwargs:
                    kwargs["output"] = self.result

                try:
                    result = agent.run(self.task, remote=self.remote, **kwargs)
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    self._handle_run_exception(exc)
                    result = None
                    exception_raised = True

        if result:
            self.cache.write(agent=self.agent, model=self.model, query=self.task, result=result)
        elif not exception_raised:
            self._handle_no_result()

        self.result = result
        print(result)
        self.is_running = False
        return self.result

    def _handle_no_result(self):
        print("No result returned")

    def _handle_no_token(self, agent):
        print(f"No token found for agent '{agent}'")

    def _handle_run_exception(self, exc: Exception):
        # openai.error.RateLimitError: You exceeded your current quota, please check your plan
        # and billing details.
        print(exc)

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__class__.__name__
