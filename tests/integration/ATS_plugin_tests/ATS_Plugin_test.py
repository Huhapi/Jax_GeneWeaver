from ATS import ATS_Plugin
import os


if __name__ == "__main__":
    this_file = os.path.abspath(__file__)
    project_root = os.path.abspath(os.path.join(this_file, "..", "..", "..", ".."))

    tests_dir = os.path.join(project_root, "tests", "unit", "MSET_tests")
    file_path_1 = os.path.join(tests_dir, "RATUS1")
    file_path_2 = os.path.join(tests_dir, "ratus2")
    background_file_path = os.path.join(tests_dir, "KEGGRattusnorvegicusBG.txt")

    input_data = {
        "tool_type": "MSET",
        "num_trials": 1000,
        "file_path_1": file_path_1,
        "file_path_2": file_path_2,
        "background_file_path": background_file_path,
        "print_to_cli": True
    }

    imp = ATS_Plugin.implement_plugins()
    print(imp.get_status())
    imp.execute(input_data)
    print(imp.get_status())
    print(imp)