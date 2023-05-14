"""Provides the TransformersAgentUI"""
import panel as pn
import param

from transformers_agent_ui.domain.agent import TransformersAgent
from transformers_agent_ui.ui.asset_editor import AssetEditor
from transformers_agent_ui.ui.config import (
    CONFIG,
    STYLES,
    TransformersAgentUIConfig,
    TransformersAgentUIStyles,
)
from transformers_agent_ui.ui.token_manager import TokenManagerUI

# Hack to fix bug similar to https://github.com/holoviz/panel/issues/4829
pn.widgets.Terminal.param.clear.readonly = False
pn.widgets.Terminal.param.clear.constant = False


class TransformersAgentUI(TransformersAgent, pn.viewable.Viewer):
    """The TransformersAgentUI makes it easy to use the Hugging Face Transformers Agent
    in your notebook or web app

    Example:

    >>> import panel as pn
    >>> from transformers_agent_ui import TransformersAgentUI
    >>> pn.extension("terminal", "notifications", notifications=True, design="bootstrap")
    >>> TransformersAgentUI()
    """

    submit = param.Event()

    config: TransformersAgentUIConfig = param.ClassSelector(
        class_=TransformersAgentUIConfig, default=CONFIG
    )
    styles: TransformersAgentUIStyles = param.ClassSelector(
        class_=TransformersAgentUIStyles, default=STYLES
    )

    def __init__(self, **params):
        if "token_manager" not in params:
            params["token_manager"] = TokenManagerUI(name="Token Manager")
        super().__init__(**params)

    def __panel__(self):
        logo = pn.pane.PNG(
            object="https://pyviz-dev.github.io/panel/_static/logo_horizontal_light_theme.png",
            link_url="https://panel.holoviz.org",
            alt_text="Power by Panel. The powerful data exploration & web app framework for Python",
            height=50,
        )

        header = pn.Row(
            f"<h1>{self.config.title_emoji} {self.config.title}</h1>",
            pn.layout.HSpacer(),
            logo,
            styles=self.styles.header_styles,
            sizing_mode="stretch_width",
            margin=0,
        )
        editor = self._create_editor()

        logs = pn.widgets.Terminal(name="Logs", sizing_mode="stretch_width")
        logs.write("Hi. The logs from your runs will be shown here!")
        # sys.stdout = self._terminal
        about = pn.pane.Markdown(self.config.about, sizing_mode="stretch_width", name="About")
        settings = pn.Column(self.token_manager, self.param.use_cache, name="Settings")

        tabs = pn.Tabs(
            editor,
            # self._results,
            logs,
            settings,
            about,
        )

        return pn.Column(
            header,
            tabs,
            sizing_mode="stretch_width",
        )

    def _create_editor(self):
        agent_input = pn.widgets.RadioButtonGroup.from_param(
            self.param.agent, margin=(5, 0), button_style="outline"
        )
        model_input = pn.widgets.RadioButtonGroup.from_param(
            self.param.model, button_style="outline"
        )
        query_input = pn.widgets.TextAreaInput.from_param(
            self.param.value,
            sizing_mode="stretch_width",
            name="Task",
            stylesheets=["textarea { font-size: 2em; }"],
        )
        submit_input = pn.widgets.Button.from_param(
            self.param.submit,
            button_type="primary",
            sizing_mode="stretch_width",
            disabled=self.param.running,
            loading=self.param.running,
            stylesheets=[self.styles.submit_button_style_sheet],
            name="SUBMIT",
        )
        task_input = pn.Column(query_input, submit_input)
        assets_input = AssetEditor()

        inputs = pn.Column(
            pn.Row(
                pn.pane.HTML(
                    "Agent",
                    styles={
                        "padding-top": "0.5em",
                    },
                ),
                agent_input,
                pn.pane.HTML(
                    "Model",
                    styles={
                        "padding-top": "0.5em",
                        "padding-left": "0.5em",
                    },
                ),
                model_input,
                align="start",
            ),
            pn.Column(
                task_input,
                "Assets",
                assets_input,
            ),
        )

        outputs = pn.panel(self._result_view, align="center")

        return pn.Row(
            pn.Column(
                "### Input",
                inputs,
                sizing_mode="stretch_width",
            ),
            pn.layout.VSpacer(width=1, styles={"background": self.styles.divider_color}),
            pn.Column(
                "### Output",
                outputs,
                sizing_mode="stretch_width",
            ),
            name="Editor",
            margin=(15, 5, 10, 5),
        )

    @param.depends("result", "running")
    def _result_view(self):
        if self.running:
            return f"""Running `{self.agent=}` and `{self.model=}` on \n\n{self.value}\n\n
Check the Logs tab for output."""
        if not self.result:
            return "Click Submit to generate an output"
        return self.result

    @pn.depends("submit", watch=True)
    def _submit(self):
        self.run()

    def _handle_no_token(self, agent):
        message = f"No token found for agent '{agent}'. Please provide one."
        print(message)
        pn.state.notifications.error(message)

    def _handle_run_exception(self, exc: Exception):
        # openai.error.RateLimitError: You exceeded your current quota, please check your plan
        # and billing details.
        print(exc)
        pn.state.notifications.error(f"The run failed: {exc}." + " Check the logs.")  # type: ignore

    def _handle_no_result(self):
        message = "No result returned"
        print(message)
        pn.state.notifications.error(message + " Check the logs.")


if pn.state.served:
    pn.extension("terminal", "notifications", notifications=True, design="bootstrap")
    TransformersAgentUI().servable()