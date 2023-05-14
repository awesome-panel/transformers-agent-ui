"""Provides the TokenManagerUI"""
import panel as pn

from transformers_agent_ui.domain.token import TokenManager


class TokenManagerUI(TokenManager, pn.viewable.Viewer):
    """Adds a UI on top of the TokenManager to enable users to manage tokens
    via environment variables or widgets"""

    def __panel__(self):
        alert = pn.pane.Alert(
            (
                "**Protect your tokens!** If you are using this tool online make sure you trust "
                "the publisher of this app before entering your tokens."
            ),
            alert_type="danger",
            margin=(0, 15),
            sizing_mode="stretch_width",
            max_width=600,
        )
        info = pn.pane.Alert(
            (
                "If the **environment variable** is set it, you don't have to specify a token to "
                "use the API."
            ),
            alert_type="dark",
            margin=(0, 15),
            sizing_mode="stretch_width",
            max_width=600,
        )
        inputs = pn.Param(
            self,
            name="Tokens",
            show_name=False,
            widgets={
                "hugging_face": {
                    "type": pn.widgets.PasswordInput,
                    "max_width": 600,
                    "sizing_mode": "stretch_width",
                },
                "open_ai": {
                    "type": pn.widgets.PasswordInput,
                    "max_width": 600,
                    "sizing_mode": "stretch_width",
                },
            },
        )
        return pn.Column(inputs, info, alert)
