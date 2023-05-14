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
    query = "Draw me a picture of rivers and lakes."

    result = image
    result = "Some text"
    # Then
    assert not store.exists(agent, model, query)
    assert not store.read(agent, model, query)

    # When/ Then
    store.write(agent, model, query, result)
    assert store.exists(agent, model, query)
    assert store.read(agent, model, query) == result

    # When/ Then
    store.delete(agent, model, query)
    assert not store.exists(agent, model, query)
    assert not store.read(agent, model, query)


def test_pickle(store):
    """We can write and read pickle"""
    agent = "A"
    model = "B"
    query = "C"
    result = pytest.fixture  # We expect this to be pickled
    with warnings.catch_warnings(record=True) as wrn:
        store.write(agent, model, query, result)
        assert len(wrn) == 1
        assert "Saved type " in str(wrn[-1].message)
    actual = store.read(agent, model, query)
    assert actual == result
