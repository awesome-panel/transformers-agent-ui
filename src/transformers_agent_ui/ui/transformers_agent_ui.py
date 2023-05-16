"""Provides the TransformersAgentUI"""
import numpy as np
import panel as pn
import param
from torch import Tensor

from transformers_agent_ui.domain.agent import TransformersAgent
from transformers_agent_ui.ui.components import (
    KwargsEditor,
    get_example_selection_widget,
)
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

    submit = param.Event(doc="Click to run the task")

    config: TransformersAgentUIConfig = param.ClassSelector(
        class_=TransformersAgentUIConfig, default=CONFIG
    )
    styles: TransformersAgentUIStyles = param.ClassSelector(
        class_=TransformersAgentUIStyles, default=STYLES
    )
    # pane_type = param.Selector(objects=[None, pn.pane.Audio])

    def __init__(self, **params):
        if "token_manager" not in params:
            params["token_manager"] = TokenManagerUI(name="Token Manager")
        super().__init__(**params)

    def __panel__(self):
        # logo = pn.pane.PNG(
        #     object="https://pyviz-dev.github.io/panel/_static/logo_horizontal_light_theme.png",
        #     link_url="https://panel.holoviz.org",
        #     height=50,
        # )

        header = pn.Row(
            f"<h1>{self.config.title_emoji} {self.config.title}</h1>",
            pn.layout.HSpacer(),
            # logo,
            styles=self.styles.header_styles,
            sizing_mode="stretch_width",
            margin=0,
        )
        editor = self._create_editor()

        logs = pn.widgets.Terminal(name="Logs", sizing_mode="stretch_width")
        logs.write("Hi. The logs from your runs will be shown here!")
        # sys.stdout = self._terminal
        about = pn.pane.Markdown(self.config.about, sizing_mode="stretch_width", name="About")
        settings = pn.Column(self.token_manager, name="Settings")

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
        show_details_input = pn.widgets.Checkbox(
            value=False,
            name="Show details",
            description="If Checked more advanced settings are show",
        )
        details = pn.Column(
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
            pn.Row(self.param.use_cache, self.param.remote, margin=(15, 5)),
            visible=show_details_input,
        )
        example_input = get_example_selection_widget(task=self)
        task_input = pn.widgets.TextAreaInput.from_param(
            self.param.task,
            sizing_mode="stretch_width",
            name="Task",
            stylesheets=["textarea { font-size: 2em; }"],
            description="A short text describing the task to run",
        )
        submit_input = pn.widgets.Button.from_param(
            self.param.submit,
            button_type="primary",
            sizing_mode="stretch_width",
            disabled=self.param.is_running,
            loading=self.param.is_running,
            stylesheets=[self.styles.submit_button_style_sheet],
            name="RUN",
        )
        task_input = pn.Column(task_input, submit_input)
        assets_input = KwargsEditor(kwargs=self.param.kwargs)

        inputs = pn.Column(
            show_details_input,
            details,
            pn.Column(
                example_input,
                task_input,
                pn.pane.HTML("Arguments", margin=(0, 10)),
                pn.pane.Alert(
                    """You can refer to *arguments* in your task by their names. For example \
                        'image'. You can  also refer to the output value on the right via the name \
                        'value'.""",
                    alert_type="warning",
                    margin=(0, 10),
                ),
                assets_input,
            ),
        )

        outputs = pn.panel(self._value_view, align="center")

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

    @param.depends("value", "is_running")
    def _value_view(self):
        if not self.is_running and self.value is None:
            return "Click RUN to generate an output"
        if self.is_running:
            return f"""Running `{self.agent=}` and `{self.model=}` on \n\n{self.task}"""

        return pn.Tabs(
            ("VALUE", self.get_value_pane),
            ("CODE", pn.widgets.Terminal(self.code)),
            ("EXPLANATION", self.explanation),
            ("PROMPT", self.prompt),
            align="center",
            sizing_mode="stretch_width",
        )

    def _get_last_tool(self) -> str:
        """Returns the last tool used in the code"""
        code = self.code

        if not code:
            return "NA"

        tools = ["text_reader"]
        last_index = {code.rindex(tool): tool for tool in tools if tool in code}
        if not last_index:
            return ""

        max_last_index = max(last_index)
        last_tool = last_index[max_last_index]

        return last_tool

    def get_value_pane(self):
        """Returns a converted value that can be displayed by Panel"""
        # Here we should help the agent return something that can be displayed
        value = self.value
        tool = self._get_last_tool()

        if tool == "text_reader":
            if isinstance(value, Tensor) and hasattr(value, "numpy"):
                value = value.numpy()  # pylint: disable=no-member
            if isinstance(value, np.ndarray) and value.dtype in (np.float32,):
                value = (value * 32768.0).astype(np.int16)
            if isinstance(value, np.ndarray):
                return pn.pane.Audio(value, sample_rate=16000)

        return value

    @pn.depends("submit", watch=True)
    def _submit(self):
        self.run()

    def _handle_no_token(self, agent):
        message = f"No token found for agent '{agent}'. Please provide one."
        print(message)
        if pn.state.notifications:
            pn.state.notifications.error(message, duration=12000)

    def _handle_run_exception(self, exc: Exception):
        # openai.error.RateLimitError: You exceeded your current quota, please check your plan
        # and billing details.
        print(exc)
        if pn.state.notifications:
            pn.state.notifications.error(f"The run failed: {exc}.", duration=12000)  # type: ignore

    def _handle_no_result(self):
        message = "No result returned"
        print(message)
        if pn.state.notifications:
            pn.state.notifications.error(message, duration=12000)


if pn.state.served:
    pn.extension("terminal", "notifications", notifications=True, design="bootstrap")
    TransformersAgentUI().servable()
