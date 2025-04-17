from ATS import ATS_Plugin
import os
from plugins.MSET import MSET
import asyncio

def test_load_plugins():
    imp = ATS_Plugin.implement_plugins()
    #print(imp.get_status())
    plugins = imp.load_plugins()
    for plug,object in enumerate(plugins):
        print("plug:",plug)
        print("obj:",plugins[object])
        if isinstance(plugins[object],MSET.MSET):
            print("MSET comparison success.")
    print(plugins)

async def test_execute(input):
    imp = ATS_Plugin.implement_plugins()
    await imp.execute(input)


async def get_info_and_execute():

    this_file = os.path.abspath(__file__)
    project_root = os.path.abspath(os.path.join(this_file, "..", "..", "..", ".."))

    tests_dir = os.path.join(project_root, "tests", "unit", "MSET_tests")
    file_path_1 = os.path.join(tests_dir, "RATUS1")
    file_path_2 = os.path.join(tests_dir, "ratus2")
    background_file_path = os.path.join(tests_dir, "KEGGRattusnorvegicusBG.txt")

    input_data = {
        "tools_input": "MSET",
        "num_trials": 1000,
        "file_path_1": file_path_1,
        "file_path_2": file_path_2,
        "background_file_path": background_file_path,
        "print_to_cli": True
    }
    test_load_plugins()
    await test_execute(input_data)

if __name__ == "__main__":
    asyncio.run(get_info_and_execute())


    
        # Code for dynamically calling plugins via yaml file.

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