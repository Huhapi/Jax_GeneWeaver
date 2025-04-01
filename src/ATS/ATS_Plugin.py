# Daniel, Anushka, Harshit, Kishan
# First attempt at factory method for plugin implementation
from typing import Any, Dict
from abc import abstractmethod
from plugins.MSET import MSET

class implement_plugins():
    @abstractmethod
    async def run(self, input_data: Dict[str, Any]):
        pass
    @abstractmethod
    def status():
        pass
    # Factory class to create plugins
    def execute(input):
        @staticmethod
        def create_plugin(input):
            if input.get("tool type") == 'MSET':
                # implement a yoml file which maps MSET to MSETTASK class
                task = MSET.MSETTask()    
                return task.run(input)
            elif input.get("tool type") == 'Boolean Algebra':
                pass
                #return PluginB(input)
            else:
                raise ValueError(f"Unknown plugin type: {plugin_type}")

