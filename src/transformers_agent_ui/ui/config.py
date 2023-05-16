"""Configuration used by the UI components

- TransformersAgentUIConfig
- TransformersAgentUIStyles
"""
# pylint: disable=too-few-public-methods
from typing import Dict

import panel as pn
import param


class TransformersAgentUIConfig:
    """Configuration settings for the UI"""

    title_emoji: str = param.String("🤗")
    title: str = param.String("Hugging Face Transformers Agent")
    # pylint: disable=line-too-long
    about: str = param.String(
        f"""The purpose of this app is to provide **an effictive user interface for the
<a href="https://huggingface.co/docs/transformers/transformers_agents" target="_blank">Hugging Face Transformer Agent</a>.**

<a href="https://panel.holoviz.org" target="_blank"><img src="https://pyviz-dev.github.io/panel/_static/logo_horizontal_light_theme.png" style="height:50px"></img></a>

Powered by <a href="https://panel.holoviz.org" target="_blank">Panel</a> v{pn.__version__}.
**The powerful data exploration & web app framework for Python**.

You can find the source code on Github at [awesome-panel/transformers-agent-ui](https://github.com/awesome-panel/transformers-agent-ui).
"""
    )
    # pylint: enable=line-too-long


HF_YELLOW = "#fef3c7"
HF_DARK_GRAY = "#4b5563"


class TransformersAgentUIStyles:
    """Style settings for the UI"""

    header_background_color: str = param.Color(HF_YELLOW)
    header_color: str = param.Color(HF_DARK_GRAY)
    accent_color: str = param.Color(HF_DARK_GRAY)
    accent_text_color: str = param.Color(HF_YELLOW)
    divider_color: str = param.Color("lightgray")

    @property
    def submit_button_style_sheet(self) -> str:
        """The style_sheet for the submit button"""
        return f"""
:host(.solid) .bk-btn.bk-btn-primary {{
  --panel-primary-color: {self.accent_color};
  --bs-btn-color: {self.accent_text_color};  
}}
"""

    @property
    def header_styles(self) -> Dict:
        """The styles for the header"""
        return {
            "background": self.header_background_color,
            "color": self.header_color,
            "padding": "10px",
        }


CONFIG = TransformersAgentUIConfig()
STYLES = TransformersAgentUIStyles()
