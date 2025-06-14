"""
Module containing the possible steps for the pipeline.
"""

from .classify_request import ClassifyRequestStep
# from .retrieve_memory import RetrieveMemoryStep
# from .select_tools import SelectToolsStep
# from .prompt_builder import PromptBuilderStep
# from .send_to_llm import SendToLLMStep

STEP_REGISTRY = {
    "classify_request": ClassifyRequestStep,
    # "retrieve_memory": RetrieveMemoryStep,
    # "select_tools": SelectToolsStep,
    # "prompt_builder": PromptBuilderStep,
    # "send_to_llm": SendToLLMStep,
}