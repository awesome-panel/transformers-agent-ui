"""We have a Parameterized wrapper for the Hugging Face Transformers Agent"""
# pylint: disable=missing-function-docstring
from transformers_agent_ui.domain.run_input import AGENT_CONFIGURATION, RunInput


def test_constructor():
    for agent, configuration in AGENT_CONFIGURATION.items():
        for model in configuration["models"]:
            app = RunInput(
                agent=agent, model=model, task="Draw me a picture", kwargs={"text": "some text"}
            )
            assert app.agent == agent
            assert app.model == model


def test_agent_and_model_change():
    app = RunInput()

    for agent, configuration in AGENT_CONFIGURATION.items():
        app.agent = agent
        for model in configuration["models"]:
            app.model = model
