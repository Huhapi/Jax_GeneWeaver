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

        returns: A dictionary of loaded plugins, the class name(as a string) of each as keys and class object as values.
        
        """
        entry_points = importlib.metadata.entry_points(group="jax.ats.plugins")
        plugins = {}
        for ep in entry_points:
            plugin_cls = ep.load()
            plugin_instance = plugin_cls()
            if isinstance(plugin_instance, implement_plugins): #implement_plugins is our interface for the plugins
                plugins[plugin_cls.__name__] = plugin_instance
            else:
                # Potentially added to return object information
                print(f"Warning: {ep.name} does not conform to plugin interface.")
        return plugins
        
    def execute(self, input):
        """ This function executes the loading of the plugins and calls the one specified in the input.
        
        input: The JSON input from the frontend interface.

        output: One of the JSON return objects. Depending on success or failure.
        """

        LOADED_PLUGINS = self.load_plugins()
        # Get specified plugin to run via input key "tool_type" representing the exact class name as a string in input dictionary
        if input["tools_input"] == "MSET":
            self.instance = LOADED_PLUGINS.get("MSETTask",None)
        
        if self.instance:
            print("Failed to load instance.")
            # Run the selected class with the input information.
            return self.instance.run(input)
        #else:
            #Return a JSON failure object with information

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

