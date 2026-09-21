##
## Original Author: https://github.com/nicekriss/toobusy, collect and organize by shines77(Guozi)
## My GitHub: https://github.com/shines77/ComfyUI-GZNodes
##
import torch

import comfy.model_management
import comfy.nested_tensor

from comfy_api.latest import io, ui

import logging

class GzMiniMaxH3ImageLatent(io.ComfyNode):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 2048, "min": 32, "max": 8192, "step": 32}),
                "height": ("INT", {"default": 2048, "min": 32, "max": 8192, "step": 32}),
            },
        }

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="GzMiniMaxH3ImageLatent",
            display_name="Guozi MiniMax H3 Image Latent",
            category="GzNodes/MiniMax-H3",
            description="Creates the one-frame video+audio latent required to run MiniMax H3 with a T=1 image VAE.",
            inputs=[
                io.Int.Input("width", default=2048, min=32, max=8192, step=32, tooltip="Output image width"),
                io.Int.Input("height", default=2048, min=32, max=8192, step=32, tooltip="Output image height"),
            ],
            outputs=[
                io.Latent.Output(display_name="samples", tooltip="Video and audio latent with a T=1 image VAE."),
            ],
        )

    @classmethod
    def execute(cls, width, height) -> io.NodeOutput:
        device = comfy.model_management.intermediate_device()
        video = torch.zeros([1, 24, 1, height // 16, width // 16], device=device)
        audio = torch.zeros([1, 32, 2, 2], device=device)
        samples = comfy.nested_tensor.NestedTensor((video, audio))
        return io.NodeOutput(samples)

NODE_CLASS_MAPPINGS = {
    "GzMiniMaxH3ImageLatent": GzMiniMaxH3ImageLatent,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GzMiniMaxH3ImageLatent": "Guozi MiniMax H3 Image Latent",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
