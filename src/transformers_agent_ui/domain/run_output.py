"""Provides the RunOutput"""
import param


class RunOutput(param.Parameterized):
    """A model of the Agent run output"""

    value = param.Parameter()

    prompt = param.String()
    explanation = param.String()
    code = param.String()
