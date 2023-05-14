"""We have a UI for the Hugging Face Transformers Agent"""
import pytest

from transformers_agent_ui import TransformersAgentUI
from transformers_agent_ui.ui.config import (
    TransformersAgentUIConfig,
    TransformersAgentUIStyles,
)


def test_constructor():
    """We can construct an instance"""
    agent = TransformersAgentUI()

    assert isinstance(agent.config, TransformersAgentUIConfig)
    assert isinstance(agent.styles, TransformersAgentUIStyles)
    assert agent.__panel__()


@pytest.mark.slow()
def test_submit():
    """We can submit a run. And do it twice"""
    agent = TransformersAgentUI()
    assert not agent.result

    agent.param.trigger("submit")
    assert agent.result

    agent.result = None
    agent.param.trigger("submit")
    assert agent.result
