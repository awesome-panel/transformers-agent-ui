"""Assets"""
from functools import cache
from pathlib import Path

from PIL import Image

ROOT_PATH = Path(__file__).parent
BOAT_IN_WATER_IMAGE_PATH = ROOT_PATH / "boat-in-water.png"
CAPYBARA_IMAGE_PATH = ROOT_PATH / "capybara.png"


@cache
def get_boat_in_water_image() -> Image.Image:
    """Returns an Image of a boat in water"""
    return Image.open(BOAT_IN_WATER_IMAGE_PATH)


@cache
def get_capybara_image() -> Image.Image:
    """Returns an Image of a beaver"""
    return Image.open(CAPYBARA_IMAGE_PATH)
