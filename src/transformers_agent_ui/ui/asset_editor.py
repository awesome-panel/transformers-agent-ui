"""Provides the AssetEditor"""
from __future__ import annotations

from typing import Dict

import panel as pn
from PIL import Image

from transformers_agent_ui.assets import IMAGE_PATH

IMAGE = Image.open(IMAGE_PATH)

DEFAULT_ASSETS = {"image": IMAGE}


class AssetEditor(pn.viewable.Viewer):
    """An editor for managing assets to be used by the agent"""

    def __init__(self, assets: Dict | None = None, **params):
        if not assets:
            assets = {}
        self._assets = assets.copy()

        super().__init__(**params)

    def __panel__(self):
        return self._layout()

    def _layout(self):
        layout = pn.Column(sizing_mode="stretch_width")
        for name, asset in self.assets.items():
            layout.append(pn.pane.Markdown(f"`{name}`", margin=(0, 10)))
            layout.append(pn.panel(asset, width=200, height=200))
        return layout

    @property
    def assets(self) -> Dict:
        """Returns the dictionary of assets"""
        return {"image": IMAGE}
