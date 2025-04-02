# Daniel, Anushka, Harshit, Kishan
# First attempt at factory method for plugin implementation
# Add pyYAML to dependencies
from typing import Any, Dict
from abc import abstractmethod
import os, yaml
import importlib
import asyncio

class implement_plugins():
    def __init__(self, input: Dict[str, Any]):
        self.instance = None
        tools_yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools.yaml")
        with open(tools_yaml_path, "r") as file:
            config=yaml.safe_load(file)
        print(config)
        className=config["tools"].get(input.get("tool type")) # "tool type" in input dictionary determines tool selection
        print(className)
        if className:
            module_path, class_name = className.rsplit(".", 1)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            print(cls)
            if cls:
                self.instance = cls()
                print(self.instance)
                result = asyncio.run(self.instance.run(input))
                print(result)
        else:
            raise ValueError(f"Unknown plugin type: {input.get("tool type")}")
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



