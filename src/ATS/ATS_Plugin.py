# Daniel, Anushka, Harshit, Kishan
# First attempt at factory method for plugin implementation
# Add pyYAML to dependencies
from typing import Any, Dict
from abc import abstractmethod
import os, yaml
import importlib
import asyncio

class implement_plugins():
    def __init__(self):
        self.instance = None

    def execute(self,input):
        tools_yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools.yaml")
        with open(tools_yaml_path, "r") as file:
            config=yaml.safe_load(file)
        tool_type = input.get("tool_type")
        className=config["tools"].get(tool_type) # "tool type" in input dictionary determines tool selection
        if className:
            module_path, class_name = className.rsplit(".", 1)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            if cls:
                self.instance = cls()
                result = asyncio.run(self.instance.run(input))
                print(result)
        else:
            raise ValueError(f"Unknown plugin type: {tool_type}")
    @abstractmethod
    def run(self, input_data: Dict[str, Any]):
        pass
    @abstractmethod
    def status(self):
        pass
    # Get status class for front end interface call
    def get_status(self):
        if self.instance:
            return self.instance.status()
        else:
            return "Initializing" # This needs to be in JSON format

