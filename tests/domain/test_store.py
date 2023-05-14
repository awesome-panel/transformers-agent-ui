"""We can store runs"""
# pylint: disable=redefined-outer-name, (missing-function-docstring
import warnings
from pathlib import Path

import pytest
from PIL import Image

from transformers_agent_ui.domain.store import Store


@pytest.fixture
def store(tmp_path):
    return Store(path=tmp_path)


@pytest.fixture
def image() -> Image.Image:
    path = Path(__file__).parent / "test_image.png"
    return Image.open(path)


def test_constructor(store):
    isinstance(store, Store)


def test_store(store, image):
    # Given
    agent = "HuggingFace"
    model = "Starcoder"
    task = "Draw me a picture of rivers and lakes."
    kwargs = {"text": "some text"}
    output = {
        "prompt": "A",
        "explanation": "B",
        "code": "C",
        "value": image,
    }
    # Then
    assert not store.exists(agent, model, task, kwargs)
    assert not store.read(agent, model, task, kwargs)

    # When/ Then
    store.write(agent, model, task, kwargs, **output)
    assert store.exists(agent, model, task, kwargs)
    assert store.read(agent, model, task, kwargs) == output

    # When/ Then
    store.delete(agent, model, task)
    assert not store.exists(agent, model, task, kwargs)
    assert not store.read(agent, model, task, kwargs)


def test_pickle(store):
    """We can write and read pickle"""
    agent = "A"
    model = "B"
    task = "C"
    kwargs = {"text": "some text"}
    output = {
        "prompt": "A",
        "explanation": "B",
        "code": "C",
        "value": pytest.fixture,  # We expect this to be pickled
    }
    with warnings.catch_warnings(record=True) as wrn:
        store.write(agent, model, task, kwargs, **output)
        assert len(wrn) == 1
        assert "Saved type " in str(wrn[-1].message)
    actual = store.read(agent, model, task, kwargs)
    assert actual == output
