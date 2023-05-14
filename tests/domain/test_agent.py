"""We have a Parameterized wrapper for the Hugging Face Transformers Agent"""
# pylint: disable=missing-function-docstring
from transformers_agent_ui.domain.agent import AGENT_CONFIGURATION, TransformersAgent


def test_constructor():
    for agent, configuration in AGENT_CONFIGURATION.items():
        for model in configuration["models"]:
            app = TransformersAgent(agent=agent, model=model, task="Draw me a picture")
            assert app.agent == agent
            assert app.model == model


def test_agent_and_model_change():
    app = TransformersAgent()

    for agent, configuration in AGENT_CONFIGURATION.items():
        app.agent = agent
        for model in configuration["models"]:
            app.model = model
