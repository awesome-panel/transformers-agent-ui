"""Configuration for the domain models"""
# pylint: disable=line-too-long
DEFAULT_AGENT = "HuggingFace"
AGENT_CONFIGURATION = {
    "HuggingFace": {
        "default": "StarcoderBase",
        "models": {
            "OpenAssistant": {
                "url_endpoint": "https://api-inference.huggingface.co/models/OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5"
            },
            "Starcoder": {
                "url_endpoint": "https://api-inference.huggingface.co/models/bigcode/starcoder"
            },
            "StarcoderBase": {
                "url_endpoint": "https://api-inference.huggingface.co/models/bigcode/starcoderbase"
            },
        },
    },
    "OpenAI": {
        "default": "text-davinci-003",
        "models": {"text-davinci-003": {"model": "text-davinci-003"}},
    },
}
