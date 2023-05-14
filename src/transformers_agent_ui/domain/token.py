"""The TokenManager enables you to manage your API tokens"""
import os

import param

HUGGING_FACE_ENV_VALUE = "HUGGING_FACE_TOKEN"
OPEN_AI_ENV_VALUE = "OPEN_AI_TOKEN"


class TokenManager(param.Parameterized):
    """The TokenManager enables you to manage your API tokens

    Either via environment variables or by setting the parameter values
    """

    hugging_face = param.String(doc="A token for the Hugging Face API", label="Hugging Face")
    hugging_face_env_exists = param.Boolean(
        constant=True,
        doc=f"True if provided by the '{HUGGING_FACE_ENV_VALUE}' environment variable",
        label=f"The '{HUGGING_FACE_ENV_VALUE}' environment variable is set",
    )
    hugging_face_env_value = param.String(
        constant=True,
        precedence=-1,
    )

    open_ai = param.String(doc="A token for the Open AI API", label="Open AI")
    open_ai_env_exists = param.Boolean(
        constant=True,
        doc=f"True if provided by the '{OPEN_AI_ENV_VALUE}' environment variable",
        label=f"The '{OPEN_AI_ENV_VALUE}' environment variable is set",
    )
    open_ai_env_value = param.String(
        constant=True, precedence=-1, label=f"{OPEN_AI_ENV_VALUE} is set"
    )

    def __init__(self, **params):
        params["hugging_face_env_value"] = os.getenv(HUGGING_FACE_ENV_VALUE, "")
        params["hugging_face_env_exists"] = bool(params["hugging_face_env_value"])

        params["open_ai_env_value"] = os.getenv(OPEN_AI_ENV_VALUE, "")
        params["open_ai_env_exists"] = bool(params["open_ai_env_value"])

        super().__init__(**params)

    def get(self, agent: str) -> str:
        """Returns the token of the agent

        If a value for the given agent is set then it is returned.
        If the environment value for the given agent is set then it is returned
        Else "" is returned
        """
        if agent == "HuggingFace":
            value = self.hugging_face
            env = self.hugging_face_env_value
        elif agent == "OpenAI":
            value = self.open_ai
            env = self.open_ai_env_value
        else:
            value = ""
            env = ""

        return value or env
