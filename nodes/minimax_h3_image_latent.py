##
## Original Author: https://github.com/nicekriss/toobusy, collect and organize by shines77(Guozi)
## My GitHub: https://github.com/shines77/ComfyUI-GZNodes
##
import torch

import comfy.model_management
import comfy.nested_tensor

import logging

class GzMiniMaxH3ImageLatent:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 2048, "min": 32, "max": 8192, "step": 32, "tooltip": "Output image width"}),
                "height": ("INT", {"default": 2048, "min": 32, "max": 8192, "step": 32, "tooltip": "Output image height"}}),
            },
        }

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "create"
    CATEGORY = "GZNodes/MiniMax-H3"
    DESCRIPTION = "Creates the one-frame video+audio latent required to run MiniMax H3 with a T=1 image VAE."

    def create(self, width, height):
        device = comfy.model_management.intermediate_device()
        video = torch.zeros([1, 24, 1, height // 16, width // 16], device=device)
        audio = torch.zeros([1, 32, 2, 2], device=device)
        return ({"samples": comfy.nested_tensor.NestedTensor((video, audio))},)

NODE_CLASS_MAPPINGS = {
    "GzMiniMaxH3ImageLatent": GzMiniMaxH3ImageLatent,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GzMiniMaxH3ImageLatent": "Guozi MiniMax H3 Image Latent",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
