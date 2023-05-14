"""Test of the components"""
from transformers_agent_ui.domain.examples import EXAMPLES, default
from transformers_agent_ui.domain.run import TaskInput
from transformers_agent_ui.ui.components import (
    KwargsEditor,
    get_example_selection_widget,
)


def test_get_example_selection_widget():
    """We can get a widget to select an example. And when selected it updates our task"""
    # Given
    task_input = TaskInput(task="some task", kwargs={})
    example_selection_widget = get_example_selection_widget(task_input)

    assert task_input.task == default.task
    assert task_input.kwargs == default.kwargs

    # When
    for example in EXAMPLES:
        example_selection_widget.value = example.name
        assert task_input.task == example.task
        assert task_input.kwargs == example.kwargs


def test_kwargs_editor():
    """We can create a KwargsEditor to display the kwargs of a TaskInput"""
    task_input = TaskInput()
    editor = KwargsEditor(task_input.param.kwargs)

    assert editor.__panel__()
