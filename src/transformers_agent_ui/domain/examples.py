"""Provides examples for testing and for the UI"""
from typing import Dict

from transformers_agent_ui.assets import get_boat_in_water_image, get_capybara_image
from transformers_agent_ui.domain.run import TaskInput

default = TaskInput(
    name="default",
    task="Draw me a picture of rivers and lakes.",
    kwargs={},
)

image_to_image = TaskInput(
    name="image to image",
    task="Transform the image so that it snows",
    kwargs={"image": get_capybara_image()},
)
image_to_text = TaskInput(
    name="image to text",
    task="Can you caption the `boat_image`?",
    kwargs={"boat_image": get_boat_in_water_image()},
)
image_to_audio = TaskInput(
    name="image to audio",
    task="Please read out loud the contents of the `boat_image`",
    kwargs={"boat_image": get_boat_in_water_image()},
)
text_to_image = TaskInput(
    name="text to image",
    task="Generate an image of a boat in the water",
    kwargs={},
)
text_to_audio = TaskInput(
    name="text to audio",
    task="Read the following text out loud",
    kwargs={
        "text": """Hi. Do you know Panel? The powerful data exploration and data app framework for \
            Python?"""
    },
)
url_to_summary_to_audio = TaskInput(
    name="url to summary to audio",
    task="Read out loud the summary of http://hf.co",
    kwargs={},
)


EXAMPLES = [
    default,
    image_to_audio,
    image_to_image,
    image_to_text,
    text_to_audio,
    text_to_image,
    url_to_summary_to_audio,
]


def get_examples_map() -> Dict[str, TaskInput]:
    """Returns a copy of the EXAMPLES"""
    return {example.name: example for example in sorted(EXAMPLES, key=lambda x: x.name)}
