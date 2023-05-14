"""Provides examples for testing and for the UI"""
from typing import Dict

from transformers_agent_ui.assets import get_boat_in_water_image
from transformers_agent_ui.domain.run import TaskInput

default = TaskInput(
    name="default",
    task="Draw me a picture of rivers and lakes.",
    kwargs={},
)

text_to_image = TaskInput(
    name="text-to-image",
    task="Generate an image of a boat in the water",
    kwargs={},
)

image_to_text = TaskInput(
    name="image-to-text",
    task="Can you caption the `boat_image`?",
    kwargs={"boat_image": get_boat_in_water_image()},
)

EXAMPLES = [
    default,
    text_to_image,
    image_to_text,
]


def get_examples_map() -> Dict[str, TaskInput]:
    """Returns a copy of the EXAMPLES"""
    return {example.name: example for example in sorted(EXAMPLES, key=lambda x: x.name)}
