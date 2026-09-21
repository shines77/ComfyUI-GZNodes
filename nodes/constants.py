##
## Original Author: https://github.com/kijai/ComfyUI-KJNodes, collect and organize by shines77(Guozi)
## My GitHub: https://github.com/shines77/ComfyUI-GZNodes
##
from comfy import model_management

import logging

class BOOLConstant:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "value": ("BOOLEAN", {"default": True}),
        },
        }
    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("value",)
    FUNCTION = "get_value"
    CATEGORY = "GZNodes/constants"
    SEARCH_ALIASES = ["boolean", "value"]

    def get_value(self, value):
        return (value,)

class INTConstant:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "value": ("INT", {"default": 0, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff}),
        },
        }
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("value",)
    FUNCTION = "get_value"
    CATEGORY = "GZNodes/constants"
    SEARCH_ALIASES = ["integer", "value"]

    def get_value(self, value):
        return (value,)

class FloatConstant:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "value": ("FLOAT", {"default": 0.0, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff, "step": 0.00001}),
        },
        }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("value",)
    FUNCTION = "get_value"
    CATEGORY = "GZNodes/constants"
    SEARCH_ALIASES = ["float", "value"]

    def get_value(self, value):
        return (round(value, 6),)

class StringConstant:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"default": '', "multiline": False}),
            }
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "passtring"
    CATEGORY = "GZNodes/constants"
    SEARCH_ALIASES = ["text", "value"]

    def passtring(self, string):
        return (string, )

class StringConstantMultiline:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"default": "", "multiline": True}),
                "strip_newlines": ("BOOLEAN", {"default": True}),
            }
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "stringify"
    CATEGORY = "GZNodes/constants"
    SEARCH_ALIASES = ["text", "value"]

    def stringify(self, string, strip_newlines):
        new_string = string
        if strip_newlines:
            new_string = new_string.replace('\n', '').strip()
        return (new_string,)
