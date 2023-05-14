"""We can manage tokens"""
import os
from unittest import mock

from transformers_agent_ui.domain.token import (
    HUGGING_FACE_ENV_VALUE,
    OPEN_AI_ENV_VALUE,
    TokenManager,
)


@mock.patch.dict(os.environ, {OPEN_AI_ENV_VALUE: "", HUGGING_FACE_ENV_VALUE: ""})
def test_token_manager():
    """The token manager works when environment variables are not provided"""
    manager = TokenManager()

    assert not manager.hugging_face_env_exists
    assert not manager.hugging_face_env_value
    assert not manager.open_ai_env_exists
    assert not manager.open_ai_env_value
    assert not manager.hugging_face
    assert not manager.open_ai
    assert not manager.get("OpenAI")
    assert not manager.get("HuggingFace")

    # When/ Then
    manager.hugging_face = "b"
    assert manager.get("HuggingFace") == "b"

    # When/ Then
    manager.open_ai = "a"
    assert manager.get("OpenAI") == "a"


@mock.patch.dict(
    os.environ,
    {OPEN_AI_ENV_VALUE: "B", HUGGING_FACE_ENV_VALUE: "A"},
)
def test_token_manager_env_set():
    """The token manager works when environment variables are provided"""
    manager = TokenManager()

    assert manager.hugging_face_env_exists
    assert manager.hugging_face_env_value == "A"
    assert manager.hugging_face == ""
    assert manager.get("HuggingFace") == "A"

    assert manager.open_ai == ""
    assert manager.open_ai_env_value == "B"
    assert manager.open_ai_env_exists
    assert manager.get("OpenAI") == "B"

    manager.hugging_face = "b"
    assert manager.get("HuggingFace") == "b"
    manager.open_ai = "a"
    assert manager.get("OpenAI") == "a"
