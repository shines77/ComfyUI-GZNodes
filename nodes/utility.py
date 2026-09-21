##
## Original Author: https://github.com/kijai/ComfyUI-GZNodes, collect and organize by shines77(Guozi)
## My GitHub: https://github.com/shines77/ComfyUI-GZNodes
##
from comfy import model_management

import os
import math
import time  ## For class Sleep
import json
import re

import logging

from comfy.comfy_types.node_typing import IO
from comfy_api.latest import io, ui

class DummyOut:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
            "any_input": (IO.ANY, ),
            }
        }

    RETURN_TYPES = (IO.ANY,)
    FUNCTION = "dummy"
    CATEGORY = "GZNodes/misc"
    OUTPUT_NODE = True
    DESCRIPTION = """
Does nothing, used to trigger generic workflow output.    
A way to get previews in the UI without saving anything to disk.
"""

    def dummy(self, any_input):
        return (any_input,)

class JoinStrings:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "delimiter": ("STRING", {"default": ' ', "multiline": False}),
            },
            "optional": {
                "string1": ("STRING", {"default": '', "forceInput": True}),
                "string2": ("STRING", {"default": '', "forceInput": True}),
            }
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "joinstring"
    CATEGORY = "GZNodes/text"

    def joinstring(self, delimiter, string1="", string2=""):
        joined_string = string1 + delimiter + string2
        return (joined_string, )
    
class JoinStringMulti:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "inputcount": ("INT", {"default": 2, "min": 2, "max": 1000, "step": 1}),
                "string_1": ("STRING", {"default": '', "forceInput": True}),
                "delimiter": ("STRING", {"default": ' ', "multiline": False}),
                "return_list": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "string_2": ("STRING", {"default": '', "forceInput": True}),
            }
    }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "combine"
    CATEGORY = "GZNodes/text"
    DESCRIPTION = """
Creates single string, or a list of strings, from  
multiple input strings.  
You can set how many inputs the node has,  
with the **inputcount** and clicking update.
"""

    def combine(self, inputcount, delimiter, **kwargs):
        string = kwargs["string_1"]
        return_list = kwargs["return_list"]
        strings = [string] # Initialize a list with the first string
        for c in range(1, inputcount):
            new_string = kwargs.get(f"string_{c + 1}", "")
            if not new_string:
                continue
            if return_list:
                strings.append(new_string) # Add new string to the list
            else:
                string = string + delimiter + new_string
        if return_list:
            return (strings,) # Return the list of strings
        else:
            return (string,) # Return the combined string

class SomethingToString:
    @classmethod
    
    def INPUT_TYPES(s):
     return {
        "required": {
        "input": (IO.ANY, ),
    },
    "optional": {
        "prefix": ("STRING", {"default": ""}),
        "suffix": ("STRING", {"default": ""}),
    }
    }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "stringify"
    CATEGORY = "GZNodes/text"
    DESCRIPTION = """
Converts any type to a string.
"""

    def stringify(self, input, prefix="", suffix=""):
        if isinstance(input, (int, float, bool, str)):
            stringified = str(input)
        elif isinstance(input, list):
            stringified = ', '.join(str(item) for item in input)
        else:
            return input,
        if prefix: # Check if prefix is not empty
            stringified = prefix + stringified # Add the prefix
        if suffix: # Check if suffix is not empty
            stringified = stringified + suffix # Add the suffix

        return (stringified,)

class WidgetToString:
    @classmethod
    def IS_CHANGED(cls,*,id,node_title,any_input,**kwargs):
        if any_input is not None and (id != 0 or node_title != ""):
            return float("NaN")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "id": ("INT", {"default": 0, "min": 0, "max": 100000, "step": 1}),
                "widget_name": ("STRING", {"multiline": False}),
                "return_all": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                         "any_input": (IO.ANY, ),
                         "node_title": ("STRING", {"multiline": False}),
                         "allowed_float_decimals": ("INT", {"default": 2, "min": 0, "max": 10, "tooltip": "Number of decimal places to display for float values"}),
                         },
            "hidden": {"extra_pnginfo": "EXTRA_PNGINFO",
                       "prompt": "PROMPT",
                       "unique_id": "UNIQUE_ID",},
        }

    RETURN_TYPES = ("STRING", )
    FUNCTION = "get_widget_value"
    CATEGORY = "GZNodes/text"
    DESCRIPTION = """
Selects a node and it's specified widget and outputs the value as a string.  
If no node id or title is provided it will use the 'any_input' link and use that node.  
To see node id's, enable "Node ID Badge Mode" in main settings.
Alternatively you can search with the node title. Node titles ONLY exist if they  
are manually edited!
'widget_name' can be a comma separated list.
The 'any_input' is required for making sure the node you want the value from exists in the workflow.
"""

    def get_widget_value(self, id, widget_name, extra_pnginfo, prompt, unique_id, return_all=False, any_input=None, node_title="", allowed_float_decimals=2):
        workflow = extra_pnginfo["workflow"]
        #print(json.dumps(workflow, indent=4))
        results = []
        node_id = link_id = subgraph_prefix = None
        link_to_node_map = {}
        node_to_subgraph_map = {}  # Track which subgraph each node belongs to

        # Parse unique_id - handle both "parent:id" format and simple int format
        if isinstance(unique_id, str) and ":" in unique_id:
            unique_id_parts = unique_id.split(":")
            unique_id_int = int(unique_id_parts[-1])  # Use the last part as the node id
            subgraph_prefix = ":".join(unique_id_parts[:-1])  # Store the parent prefix (e.g., "14")
        else:
            unique_id_int = int(unique_id)

        # Collect all nodes from main workflow and subgraphs
        all_nodes = list(workflow.get("nodes", []))
        definitions = workflow.get("definitions", {})
        subgraphs = definitions.get("subgraphs", [])

        # Find which main workflow node references each subgraph
        subgraph_id_to_parent = {}
        for node in workflow.get("nodes", []):
            node_type = node.get("type", "")
            # Subgraph nodes have a UUID as their type
            if "-" in node_type and len(node_type) == 36:  # UUID format check
                subgraph_id_to_parent[node_type] = node["id"]

        for subgraph in subgraphs:
            subgraph_id = subgraph.get("id", "")
            parent_node_id = subgraph_id_to_parent.get(subgraph_id)

            subgraph_nodes = subgraph.get("nodes", [])
            for node in subgraph_nodes:
                # Track which subgraph (parent node) this node belongs to
                if parent_node_id is not None:
                    node_to_subgraph_map[node["id"]] = parent_node_id
            all_nodes.extend(subgraph_nodes)

            # Also build link_to_node_map from subgraph links
            subgraph_links = subgraph.get("links", [])
            for link in subgraph_links:
                # link format: [link_id, origin_id, origin_slot, target_id, target_slot, type]
                if isinstance(link, dict):
                    link_to_node_map[link["id"]] = link["origin_id"]
                elif isinstance(link, list) and len(link) >= 2:
                    link_to_node_map[link[0]] = link[1]

        for node in all_nodes:
            if node_title:
                if "title" in node:
                    if node["title"] == node_title:
                        node_id = node["id"]
                        break
                else:
                    logging.warning("Node title not found.")
            elif id != 0:
                if node["id"] == id:
                    node_id = id
                    break
            elif any_input is not None:
                if node["type"] == "WidgetToString" and node["id"] == unique_id_int and not link_id:
                    for node_input in node["inputs"]:
                        if node_input["name"] == "any_input":
                            link_id = node_input["link"]

                # Construct a map of links to node IDs for future reference
                node_outputs = node.get("outputs", None)
                if not node_outputs:
                    continue
                for output in node_outputs:
                    node_links = output.get("links", None)
                    if not node_links:
                        continue
                    for link in node_links:
                        link_to_node_map[link] = node["id"]
                        if link_id and link == link_id:
                            break

        if link_id:
            node_id = link_to_node_map.get(link_id, None)

        if node_id is None:
            raise ValueError("No matching node found for the given title or id")

        # Determine the correct prompt key
        # First check if the target node is in a subgraph
        target_subgraph_parent = node_to_subgraph_map.get(node_id)

        if target_subgraph_parent is not None:
            # Target node is in a subgraph, use the parent node id as prefix
            prompt_key = f"{target_subgraph_parent}:{node_id}"
        elif subgraph_prefix is not None:
            # We're in a subgraph, use our prefix
            prompt_key = f"{subgraph_prefix}:{node_id}"
        else:
            prompt_key = str(node_id)

        # Try the prefixed key first, then fall back to just the node_id
        if prompt_key not in prompt:
            prompt_key = str(node_id)

        if prompt_key not in prompt:
            raise KeyError(f"Node not found in prompt. Tried keys: '{target_subgraph_parent}:{node_id}' and '{node_id}'")

        values = prompt[prompt_key]
        if "inputs" in values:
            inputs = values["inputs"]

            # support comma-separated list and trim whitespace
            widget_names = []
            if widget_name:
                widget_names = [w.strip() for w in widget_name.split(",") if w.strip()]

            if return_all:
                # Format items based on type
                formatted_items = []
                for k, v in inputs.items():
                    if isinstance(v, float):
                        item = f"{k}: {v:.{allowed_float_decimals}f}"
                    else:
                        item = f"{k}: {str(v)}"
                    formatted_items.append(item)
                results.append(", ".join(formatted_items))

            # Single widget name (trimmed)
            elif len(widget_names) == 1:
                name = widget_names[0]
                if name in inputs:
                    v = inputs[name]
                    if isinstance(v, float):
                        v = f"{v:.{allowed_float_decimals}f}"
                    else:
                        v = str(v)
                    return (v, )
                else:
                    raise NameError(f"Widget not found: {node_id}.{name}")

            # Multiple widget names: return "name: value" pairs
            elif len(widget_names) > 1:
                formatted_items = []
                for name in widget_names:
                    if name not in inputs:
                        raise NameError(f"Widget not found: {node_id}.{name}")
                    v = inputs[name]
                    if isinstance(v, float):
                        v = f"{v:.{allowed_float_decimals}f}"
                    else:
                        v = str(v)
                    formatted_items.append(f"{name}: {v}")
                return (", ".join(formatted_items), )

            else:
                # No valid widget name provided
                raise NameError(f"Widget not found: {node_id}.{widget_name}")

        return (", ".join(results).strip(", "), )

class StringToFloatList:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {
                     "string" :("STRING", {"default": "1, 2, 3", "multiline": True}),
                     }
                }
    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("FLOAT",)
    CATEGORY = "GZNodes/misc"
    FUNCTION = "createlist"

    def createlist(self, string):
        float_list = [float(x.strip()) for x in string.split(',')]
        return (float_list,)

class AppendStringsToList:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string1": ("STRING", {"default": '', "forceInput": True}),
                "string2": ("STRING", {"default": '', "forceInput": True}),
            }
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "joinstring"
    CATEGORY = "GZNodes/text"

    def joinstring(self, string1, string2):
        if not isinstance(string1, list):
            string1 = [string1]
        if not isinstance(string2, list):
            string2 = [string2]
        
        joined_string = string1 + string2
        return (joined_string, )

class SaveStringKJ:
    ALLOWED_EXTENSIONS = [".txt", ".caption", ".json", ".yaml", ".yml", ".md", ".csv", ".tsv", ".xml", ".log", ".ini", ".toml"]

    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string": ("STRING", {"forceInput": True, "tooltip": "string to save as .txt file"}),
                "filename_prefix": ("STRING", {"default": "text", "tooltip": "The prefix for the file to save. This may include formatting information such as %date:yyyy-MM-dd% or %Empty Latent Image.width% to include values from nodes."}),
                "output_folder": ("STRING", {"default": "output", "tooltip": "Subfolder within the ComfyUI output directory to save to. Paths resolving outside the output directory are rejected."}),
            },
            "optional": {
                "file_extension": ("STRING", {"default": ".txt", "tooltip": "The extension for the saved file. Limited to plain-text/data formats."}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename",)
    FUNCTION = "save_string"

    OUTPUT_NODE = True

    CATEGORY = "GZNodes/misc"
    DESCRIPTION = "Saves the input string to your ComfyUI output directory."

    def save_string(self, string, output_folder, filename_prefix="text", file_extension=".txt"):
        filename_prefix += self.prefix_append

        output_dir = os.path.abspath(self.output_dir)
        if output_folder and output_folder != "output":
            sub = os.path.splitdrive(output_folder)[1].replace("\\", "/").lstrip("/")
            target_dir = os.path.abspath(os.path.join(output_dir, sub))
        else:
            target_dir = output_dir

        try:
            inside = os.path.commonpath((output_dir, target_dir)) == output_dir
        except ValueError:
            inside = False
        if not inside:
            raise ValueError(f"output_folder must resolve within the ComfyUI output directory: {target_dir}")
        os.makedirs(target_dir, exist_ok=True)

        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, target_dir)

        file_extension = os.path.basename(file_extension)
        if file_extension and not file_extension.startswith("."):
            file_extension = "." + file_extension

        if file_extension.lower() not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Disallowed file extension '{file_extension}'. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}")

        base_file_name = f"{filename_prefix}_{counter:05}_"

        txt_file = base_file_name + file_extension
        file_path = os.path.join(full_output_folder, txt_file)
        while os.path.exists(file_path):
            counter += 1
            base_file_name = f"{filename_prefix}_{counter:05}_"
            txt_file = base_file_name + file_extension
            file_path = os.path.join(full_output_folder, txt_file)

        if os.path.commonpath((os.path.abspath(full_output_folder), os.path.abspath(file_path))) != os.path.abspath(full_output_folder):
            raise ValueError(f"Refusing to write outside the target folder: {file_path}")
        with open(file_path, 'w', encoding="utf-8") as f:
            f.write(string)

        return file_path,

class SimpleCalculatorKJ(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        template = io.Autogrow.TemplateNames(input=io.MultiType.Input("var", [io.Int, io.Float, io.Boolean], optional=True), names=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"], min=2)
        return io.Schema(
            node_id="SimpleCalculatorKJ",
            category="GZNodes/misc",
            description="""
Calculator node that evaluates a mathematical expression using inputs a and b.  
    Supported operations: +, -, *, /, //, %, **, <<, >>, unary +/-  
    Supported comparisons: ==, !=, <, <=, >, >=  
    Supported logic: and, or, not  
    Supported functions: abs(), round(), min(), max(), pow(), sqrt(), sin(), cos(), tan(), log(), log10(), exp(), floor(), ceil()  
    Supported constants: pi, euler, True, False  
""",
            search_aliases=["math", "arithmetic", "expression", "logic"],
            inputs=[
                io.String.Input("expression", default="a + b", multiline=True),
                io.Autogrow.Input("variables", template=template),
            ],
            outputs=[
                io.Float.Output(),
                io.Int.Output(),
                io.Boolean.Output(),
            ],
        )

    @classmethod
    def execute(cls, variables, expression, a=None, b=None) -> io.NodeOutput:
        import ast
        import operator

        # Allowed operations
        allowed_operators = {
            ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow, 
            ast.USub: operator.neg, ast.UAdd: operator.pos, ast.LShift: operator.lshift, 
            ast.RShift: operator.rshift, ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
            ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge, ast.And: operator.and_, 
            ast.Or: operator.or_, ast.Not: operator.not_,
        }

        # Allowed functions
        allowed_functions = {
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'pow': pow, 'sqrt': math.sqrt, 'sin': math.sin,
            'cos': math.cos, 'tan': math.tan, 'log': math.log,
            'log10': math.log10, 'exp': math.exp, 'floor': math.floor,
            'ceil': math.ceil
        }

        # Allowed constants - start with pi, e, True, False
        allowed_names = {'pi': math.pi, 'euler': math.e, 'True': True, 'False': False}

        # Add all variables from autogrow to allowed_names
        for var_name, var_value in variables.items():
            allowed_names[var_name] = var_value

        # Backwards compatibility: add a and b if they're provided (for old workflows)
        if a is not None:
            allowed_names['a'] = a
        if b is not None:
            allowed_names['b'] = b

        def eval_node(node):
            if isinstance(node, ast.Constant):  # Numbers and booleans
                return node.value
            elif isinstance(node, ast.Name):  # Variables
                if node.id in allowed_names:
                    return allowed_names[node.id]
                raise ValueError(f"Name '{node.id}' is not allowed")
            elif isinstance(node, ast.BinOp):  # Binary operations
                if type(node.op) not in allowed_operators:
                    raise ValueError(f"Operator {type(node.op).__name__} is not allowed")
                left = eval_node(node.left)
                right = eval_node(node.right)
                return allowed_operators[type(node.op)](left, right)
            elif isinstance(node, ast.UnaryOp):  # Unary operations
                if type(node.op) not in allowed_operators:
                    raise ValueError(f"Operator {type(node.op).__name__} is not allowed")
                operand = eval_node(node.operand)
                return allowed_operators[type(node.op)](operand)
            elif isinstance(node, ast.Compare):  # Comparison operations
                left = eval_node(node.left)
                for op, comparator in zip(node.ops, node.comparators):
                    if type(op) not in allowed_operators:
                        raise ValueError(f"Operator {type(op).__name__} is not allowed")
                    right = eval_node(comparator)
                    result = allowed_operators[type(op)](left, right)
                    if not result:
                        return False
                    left = right
                return True
            elif isinstance(node, ast.BoolOp):  # Boolean operations (and, or)
                if type(node.op) not in allowed_operators:
                    raise ValueError(f"Operator {type(node.op).__name__} is not allowed")
                values = [eval_node(value) for value in node.values]
                if isinstance(node.op, ast.And):
                    return all(values)
                elif isinstance(node.op, ast.Or):
                    return any(values)
            elif isinstance(node, ast.Call):  # Function calls
                if not isinstance(node.func, ast.Name):
                    raise ValueError("Only simple function calls are allowed")
                if node.func.id not in allowed_functions:
                    raise ValueError(f"Function '{node.func.id}' is not allowed")
                args = [eval_node(arg) for arg in node.args]
                return allowed_functions[node.func.id](*args)
            else:
                raise ValueError(f"Node type {type(node).__name__} is not allowed")

        try:
            tree = ast.parse(expression, mode='eval')
            result = eval_node(tree.body)
            return io.NodeOutput(float(result), int(result), bool(result))
        except Exception as e:
            logging.error(f"CalculatorKJ Error: {str(e)}")
            return io.NodeOutput(0.0, 0, False)

class Sleep:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input": (IO.ANY, ),
                "minutes": ("INT", {"default": 0, "min": 0, "max": 1439}),
                "seconds": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 59.99, "step": 0.01}),
            },
        }
    RETURN_TYPES = (IO.ANY,)
    FUNCTION = "sleepdelay"
    CATEGORY = "GZNodes/misc"
    DESCRIPTION = """
Delays the execution for the input amount of time.
"""

    def sleepdelay(self, input, minutes, seconds):
        total_seconds = minutes * 60 + seconds
        time.sleep(total_seconds)
        return input,

class VRAM_Debug:
    
    @classmethod
    
    def INPUT_TYPES(s):
      return {
        "required": {
            
            "empty_cache": ("BOOLEAN", {"default": True}),
            "gc_collect": ("BOOLEAN", {"default": True}),
            "unload_all_models": ("BOOLEAN", {"default": False}),
        },
        "optional": {
            "any_input": (IO.ANY,),
            "image_pass": ("IMAGE",),
            "model_pass": ("MODEL",),
        }
	}
        
    RETURN_TYPES = (IO.ANY, "IMAGE","MODEL","INT", "INT",)
    RETURN_NAMES = ("any_output", "image_pass", "model_pass", "freemem_before", "freemem_after")
    FUNCTION = "VRAMdebug"
    CATEGORY = "GZNodes/memory"
    DESCRIPTION = """
Returns the inputs unchanged, they are only used as triggers,  
and performs comfy model management functions and garbage collection,  
reports free VRAM before and after the operations.
"""

    def VRAMdebug(self, gc_collect, empty_cache, unload_all_models, image_pass=None, model_pass=None, any_input=None):
        freemem_before = model_management.get_free_memory()
        logging.info(f"VRAMdebug: free memory before: {freemem_before:,.0f}")
        if empty_cache:
            model_management.soft_empty_cache()
        if unload_all_models:
            model_management.unload_all_models()
        if gc_collect:
            import gc
            gc.collect()
        freemem_after = model_management.get_free_memory()
        logging.info(f"VRAMdebug: free memory after: {freemem_after:,.0f}")
        logging.info(f"VRAMdebug: freed memory: {freemem_after - freemem_before:,.0f}")
        return {"ui": {
            "text": [f"{freemem_before:,.0f}x{freemem_after:,.0f}"]}, 
            "result": (any_input, image_pass, model_pass, freemem_before, freemem_after) 
        }
