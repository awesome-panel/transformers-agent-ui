"""Provides the RunInput, RunOutput and Run"""
import param

from transformers_agent_ui.domain.config import AGENT_CONFIGURATION, DEFAULT_AGENT


class AgentInput(param.Parameterized):
    """A Model of the input arguments of a task"""

    agent = param.Selector(default=DEFAULT_AGENT, objects=sorted(AGENT_CONFIGURATION.keys()))
    model = param.Selector(
        default=AGENT_CONFIGURATION[DEFAULT_AGENT]["default"],
        objects=sorted(AGENT_CONFIGURATION[DEFAULT_AGENT]["models"]),
    )

    def __init__(self, **params):
        if "agent" in params:
            agent = params["agent"]
            self.param.agent.default = agent
            self.param.model.objects = sorted(AGENT_CONFIGURATION[agent]["models"])
            self.param.model.default = AGENT_CONFIGURATION[agent]["default"]
        if "model" in params:
            self.param.model.default = params["model"]
        super().__init__(**params)

    @param.depends("agent", watch=True)
    def _handle_agent_change(self):
        configuration = AGENT_CONFIGURATION[self.agent]
        self.param.model.objects = sorted(configuration["models"])
        self.param.model.default = configuration["default"]
        self.model = AGENT_CONFIGURATION[self.agent]["default"]


class TaskInput(param.Parameterized):
    """A Model of the input arguments of a task"""

    task = param.String()
    kwargs = param.Dict()

    def __init__(self, **params):
        if "kwargs" not in params:
            params["kwargs"] = {}
        super().__init__(**params)


class RunInput(AgentInput, TaskInput):
    """A Model of the input arguments of a run"""


class RunOutput(param.Parameterized):
    """A model of the Agent run output"""

    value = param.Parameter()

    prompt = param.String()
    explanation = param.String()
    code = param.String()


class Run(RunInput, RunOutput):
    """A Model of the input and output arguments of a run"""
