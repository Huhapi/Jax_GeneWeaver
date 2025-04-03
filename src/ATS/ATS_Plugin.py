# Daniel, Anushka, Harshit, Kishan
# First attempt at factory method for plugin implementation
# Add pyYAML to dependencies
from typing import Any, Dict
from abc import abstractmethod
import importlib.metadata
import asyncio

class implement_plugins():
    def __init__(self):
        self.instance = None

    
    def load_plugins(self):
        """ This function loads the plugins through the entry points in our pypoetry.toml file.
        
        input: Nothing, but requires list of plugins with their position in the project in pypoetry.toml

        returns: A list of loaded plugins.
        
        """
        entry_points = importlib.metadata.entry_points(group="jax.ats.plugins")
        plugins = []
        for ep in entry_points:
            plugin_cls = ep.load()
            plugin_instance = plugin_cls()
            if isinstance(plugin_instance, implement_plugins): #implement_plugins is the interface for the plugins
                plugins.append(plugin_instance)
            else:
                print(f"Warning: {ep.name} does not conform to plugin interface.")
        return plugins
        
    def execute(self, input):
        """ This function executes the loading of the plugins and calls the one specified in the input.
        
        input: The JSON input from the frontend interface.

        output: One of the return objects.
        """
        LOADED_PLUGINS = self.load_plugins()

        # tools_yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools.yaml")
        # with open(tools_yaml_path, "r") as file:
        #     config=yaml.safe_load(file)
        # tool_type = input.get("tool_type")
        # className=config["tools"].get(tool_type) # "tool type" in input dictionary determines tool selection
        # if className:
        #     module_path, class_name = className.rsplit(".", 1)
        #     module = importlib.import_module(module_path)
        #     cls = getattr(module, class_name)
        #     if cls:
        #         self.instance = cls()
        #         result = asyncio.run(self.instance.run(input))
        #         print(result)
        # else:
        #     raise ValueError(f"Unknown plugin type: {tool_type}")
    @abstractmethod
    def run(self, input_data: Dict[str, Any]):
        """ This function must be implemented by any plugin which inherets this class implement_plugins"""
        pass
    @abstractmethod
    def status(self):
        """ This function must be implemented by any plugin which inherets this class implement_plugins"""
        pass
    # Get status class for front end interface call
    def get_status(self):
        if self.instance:
            return self.instance.status()
        else:
            return "Initializing" # This needs to be an error object.

