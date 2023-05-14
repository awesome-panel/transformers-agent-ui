"""Provides the TransformersAgent

A wrapper of the Hugging Face transformers agent. See
https://huggingface.co/docs/transformers/transformers_agents
"""
import logging
from datetime import datetime

import param
from transformers import HfAgent, OpenAiAgent

from transformers_agent_ui.domain.config import AGENT_CONFIGURATION, DEFAULT_AGENT
from transformers_agent_ui.domain.store import Store
from transformers_agent_ui.domain.token import TokenManager

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


class TransformersAgent(param.Parameterized):
    """A wrapper of the Hugging Face transformers agent. See
    https://huggingface.co/docs/transformers/transformers_agents"""

    agent = param.Selector(default=DEFAULT_AGENT, objects=sorted(AGENT_CONFIGURATION.keys()))
    model = param.Selector(
        default=AGENT_CONFIGURATION[DEFAULT_AGENT]["default"],
        objects=sorted(AGENT_CONFIGURATION[DEFAULT_AGENT]["models"]),
    )
    value = param.String("Draw me a picture of rivers and lakes.", label="Task")
    assets = param.Dict()

    result = param.Parameter(precedence=-1)
    running = param.Boolean()

    use_cache: bool = param.Boolean(
        default=True, doc="If True a Cache is used to speed up run and to bring the the costs."
    )
    cache: Store = param.ClassSelector(class_=Store, precedence=-1)
    token_manager: TokenManager = param.ClassSelector(class_=TokenManager, precedence=-1)

    def __init__(self, **params):
        if "agent" in params:
            agent = params["agent"]
            self.param.agent.default = agent
            self.param.model.objects = sorted(AGENT_CONFIGURATION[agent]["models"])
            self.param.model.default = AGENT_CONFIGURATION[agent]["default"]
        if "model" in params:
            self.param.model.default = params["model"]
        if "cache" not in params:
            params["cache"] = Store()
        if "token_manager" not in params:
            params["token_manager"] = TokenManager()
        super().__init__(**params)

    @param.depends("agent", watch=True)
    def _handle_agent_change(self):
        configuration = AGENT_CONFIGURATION[self.agent]
        self.param.model.objects = sorted(configuration["models"])
        self.param.model.default = configuration["default"]
        self.model = AGENT_CONFIGURATION[self.agent]["default"]

    def get_token(self) -> str:
        """Returns the token"""
        return self.token_manager.get(self.agent)

    def get_agent(self, token: str):
        """Returns the Agent"""
        return _get_agent(agent=self.agent, model=self.model, token=token)

    def run(self):
        """Runs the agent, model on the `value`"""
        exception_raised = False
        self.running = True
        if self.use_cache and self.cache.exists(
            agent=self.agent, model=self.model, query=self.value
        ):
            result = self.cache.read(agent=self.agent, model=self.model, query=self.value)
            print(
                f"{datetime.now()} Cache hit for agent='{self.agent}', model='{self.model}' "
                f"and query='{self.value}'"
            )
        else:
            token = self.get_token()
            if not token:
                self._handle_no_token(self.agent)
                result = None
                exception_raised = True
            else:
                agent = self.get_agent(token=token)
                try:
                    result = agent.run(self.value, remote="True")
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    self._handle_run_exception(exc)
                    result = None
                    exception_raised = True

        if result:
            self.cache.write(agent=self.agent, model=self.model, query=self.value, result=result)
        elif not exception_raised:
            self._handle_no_result()

        self.result = result
        print(result)
        self.running = False
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
