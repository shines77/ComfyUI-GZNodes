"""ComfyUI custom node package entrypoint.

This repository is intended to be cloned into ComfyUI's `custom_nodes` folder
(e.g. `custom_nodes/ComfyUI-GZNodes`). ComfyUI imports that folder as a Python package,
so this top-level `__init__.py` must expose node mappings.

Each sub-package is imported in isolation. A package that cannot be imported --
usually because one of its optional dependencies is missing -- is skipped on its
own, and every other toobusy node still reaches ComfyUI. The skipped packages
are reported once at the end of this module so the reason shows up in the
ComfyUI startup log instead of silently removing the whole node set.
"""
## constants
from .nodes.constants import (
    BOOLConstant, INTConstant, FloatConstant, StringConstant, StringConstantMultiline,
)

## conditioning
from .nodes.conditioning import (
    CondPassThrough, ModelPassThrough, ConditioningMultiCombine,
    ConditioningSetMaskAndCombine, ConditioningSetMaskAndCombine3,
    ConditioningSetMaskAndCombine4, ConditioningSetMaskAndCombine5,
)

## utility
from .nodes.utility import (
    DummyOut, JoinStrings, JoinStringMulti,
    SomethingToString, WidgetToString,
    StringToFloatList, AppendStringsToList,
    SaveStringKJ,
    SimpleCalculatorKJ, Sleep, VRAM_Debug,
)

import logging

logger = logging.getLogger(__name__)

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Sub-packages that imported cleanly, in registration order.
LOADED_NODE_PACKAGES = []
# Sub-package name -> the exception that stopped it from loading.
UNAVAILABLE_NODE_PACKAGES = {}

NODE_CONFIG = {
    ## constants
    "BOOLConstant": {"class": BOOLConstant, "name": "BOOL Constant"},
    "INTConstant": {"class": INTConstant, "name": "INT Constant"},
    "FloatConstant": {"class": FloatConstant, "name": "Float Constant"},
    "StringConstant": {"class": StringConstant, "name": "String Constant"},
    "StringConstantMultiline": {"class": StringConstantMultiline, "name": "String Constant Multiline"},

    ## conditioning
    "CondPassThrough": {"class": CondPassThrough, "name": "Cond Pass Through"},
    "ModelPassThrough": {"class": ModelPassThrough, "name": "Model Pass Through"},
    "ConditioningMultiCombine": {"class": ConditioningMultiCombine, "name": "Conditioning Multi Combine"},
    "ConditioningSetMaskAndCombine": {"class": ConditioningSetMaskAndCombine, "name": "ConditioningSetMaskAndCombine"},
    "ConditioningSetMaskAndCombine3": {"class": ConditioningSetMaskAndCombine3, "name": "ConditioningSetMaskAndCombine3"},
    "ConditioningSetMaskAndCombine4": {"class": ConditioningSetMaskAndCombine4, "name": "ConditioningSetMaskAndCombine4"},
    "ConditioningSetMaskAndCombine5": {"class": ConditioningSetMaskAndCombine5, "name": "ConditioningSetMaskAndCombine5"},

    ## utility
    "DummyOut": {"class": DummyOut, "name": "Dummy Out"},
    "JoinStrings": {"class": JoinStrings, "name": "Join Strings"},
    "JoinStringMulti": {"class": JoinStringMulti, "name": "Join String Multi"},
    "SomethingToString": {"class": SomethingToString, "name": "Something To String"},
    "WidgetToString": {"class": WidgetToString, "name": "Widget To String"},
    "StringToFloatList": {"class": StringToFloatList, "name": "String to Float List"},
    "AppendStringsToList": {"class": AppendStringsToList, "name": "Append Strings To List"},
    "SaveStringKJ": {"class": SaveStringKJ, "name": "Save String KJ"},   
    "SimpleCalculatorKJ": {"class": SimpleCalculatorKJ, "name": "Simple Calculator KJ"},
    "Sleep": {"class": Sleep, "name": "Sleep"},
    "VRAM_Debug": {"class": VRAM_Debug, "name": "VRAM Debug"},
}

## minimax-h3: minimax_h3_image_latent
try:
    ## from .nodes.minimax_h3_image_latent import (
    ##     NODE_CLASS_MAPPINGS as _CLASSES,
    ##     NODE_DISPLAY_NAME_MAPPINGS as _NAMES,
    ## )
    from .nodes.minimax_h3_image_latent import GzMiniMaxH3ImageLatent
except Exception as ex:
    logger.warning(f"GZNodes: MiniMax H3 nodes could not be imported. MiniMax nodes will be unavailable. Error: {e}", exc_info=True)
    UNAVAILABLE_NODE_PACKAGES["minimax_h3_image_latent"] = f"GZNodes: MiniMax H3 nodes could not be imported. MiniMax H3 nodes will be unavailable. Error: {e}"
else:
    ## NODE_CLASS_MAPPINGS.update(_CLASSES)
    ## NODE_DISPLAY_NAME_MAPPINGS.update(_NAMES)
    NODE_CONFIG.update({
        "GzMiniMaxH3ImageLatent": {"class": GzMiniMaxH3ImageLatent, "name": "Guozi MiniMax H3 Image Latent"},
    })
    LOADED_NODE_PACKAGES.append("minimax_h3_image_latent")

def generate_node_mappings(node_config):
    node_class_mappings = {}
    node_display_name_mappings = {}

    for node_name, node_info in node_config.items():
        node_class_mappings[node_name] = node_info["class"]
        node_display_name_mappings[node_name] = node_info.get("name", node_info["class"].__name__)

    return node_class_mappings, node_display_name_mappings

NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS = generate_node_mappings(NODE_CONFIG)

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
