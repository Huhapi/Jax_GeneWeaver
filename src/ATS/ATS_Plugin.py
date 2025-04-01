# Daniel, Anushka, Harshit, Kishan
# First attempt at factory method for plugin implementation
from typing import Any, Dict
from abc import abstractmethod
import os, yaml
import importlib
import asyncio

class implement_plugins():
    @abstractmethod
    def run(self, input_data: Dict[str, Any]):
        pass
    @abstractmethod
    def status(self):
        pass
    # Factory class to create plugins
    def execute(self,input):
        @staticmethod
        def create_plugin(input):
            # if input.get("tool type") == 'MSET':
            #     # implement a yoml file which maps MSET to MSETTASK class
            #     task = MSET.MSETTask()
            #     return task.run(input)
            # elif input.get("tool type") == 'Boolean Algebra':
            #     pass
            #     #return PluginB(input)
            tools_yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools.yaml")
            with open(tools_yaml_path, "r") as file:
                config=yaml.safe_load(file)
            print(config)
            className=config["tools"].get(input.get("tool type"))
            print(className)
            if className:
                module_path, class_name = className.rsplit(".", 1)
                module = importlib.import_module(module_path)
                cls = getattr(module, class_name)
                print(cls)
                if cls:
                    instance = cls()
                    print(instance)
                    result = asyncio.run(instance.run(input))
                    print(result)
            else:
                raise ValueError(f"Unknown plugin type: {plugin_type}")
        create_plugin(input)


