import panel as pn
from transformers_agent_ui import TransformersAgentUI

if pn.state.served:
    pn.extension("terminal", "notifications", notifications=True, design="bootstrap")
    TransformersAgentUI().servable()
