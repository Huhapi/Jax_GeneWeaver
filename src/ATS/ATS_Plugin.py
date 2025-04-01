# Daniel, Anushka, Harshit, Kishan
# First attempt at factory method for plugin implementation
from typing import Any, Dict
from abc import abstractmethod
from plugins.MSET import MSET
# from plugins.BooleanAlgebra import BA
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
            with open("../tools.yaml","r") as file:
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

if __name__=="__main__":
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(src_dir)
    project_root= os.path.abspath(os.path.join(project_root, ".."))
    tests_dir = os.path.join(project_root, "tests")

    file_path_1 = os.path.join(tests_dir, "unit", "MSET_tests", "RATUS1")
    file_path_2 = os.path.join(tests_dir, "unit", "MSET_tests", "ratus2")
    background_file_path = os.path.join(tests_dir,"unit","MSET_tests","KEGGRattusnorvegicusBG.txt")

    # Prepare the input data. Notice that we include the background_file_path.
    input_data = {
        "tool type": "MSET",
        "num_trials": 1000,
        "file_path_1": file_path_1,
        "file_path_2": file_path_2,
        "background_file_path": background_file_path,
        # "representation": "over",  # Optional; if omitted, it defaults to "over"
        "print_to_cli": True
    }
    imp=implement_plugins()
    imp.execute(input_data)


