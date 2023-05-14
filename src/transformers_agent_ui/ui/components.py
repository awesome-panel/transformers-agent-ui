"""Custom components for the UI"""
from __future__ import annotations

from typing import Dict

import panel as pn
import param

from transformers_agent_ui.domain.examples import get_examples_map
from transformers_agent_ui.domain.run import TaskInput


def get_example_selection_widget(task: TaskInput, select_default=True):
    """Returns a widget from which the user can select examples. When the selection changes
    the task is updated with the settings from the selected example"""
    examples_map = get_examples_map()
    examples_names = list(examples_map)
    example_selection_widget = pn.widgets.Select(
        options=examples_names,
        name="Example",
        description="When the selection changes, the example is copied to the task.",
    )

    @pn.depends(example_selection_widget, watch=True)
    def copy_example_to_task(name: str):
        example = examples_map[name]

        task.task = example.task
        task.kwargs = example.kwargs

    if select_default:
        example_selection_widget.param.trigger("value")

    return example_selection_widget


class KwargsEditor(pn.viewable.Viewer):
    """An editor for displaying and editing the kwargs of a TaskInput"""

    def __init__(self, kwargs: param.Dict, **params):
        self._panel = pn.bind(self._get_panel, kwargs=kwargs)

        super().__init__(**params)

    def __panel__(self):
        return self._panel

    def _get_panel(self, kwargs: Dict):
        layout = pn.Column(sizing_mode="stretch_width")
        for name, kwarg in kwargs.items():
            layout.append(pn.pane.Markdown(f"`{name}`", margin=(0, 10)))
            layout.append(pn.panel(kwarg, width=200, height=200))
        return layout
