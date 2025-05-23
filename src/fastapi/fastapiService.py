import asyncio
import os,shutil
from typing import Literal, Optional, List, Callable
from threading import Thread, Lock
import uuid, inspect

import starlette.datastructures
from starlette.responses import JSONResponse

from ATS import ATS_Plugin

import yaml
from fastapi import FastAPI, UploadFile, File, Form, Depends

from pydantic import BaseModel


class LoadPluginModel(BaseModel):
    tool_type: Literal["MSET","Boolean"]
    num_trials: Optional[int]= 1000
    print_to_cli: Optional[bool]= True
    gene_set_ids: Optional[List[str]] = list

UPLOAD_DIR = os.getcwd()

app = FastAPI()

class FileMetadata(BaseModel):
    title: str
    description: str

# Function to extract metadata from form fields
def parse_metadata(
        tool_type: str = Form(...),
        num_trials: Optional[int] = Form(1000),
        print_to_cli: Optional[bool]=Form(True),
        gene_set_ids: Optional[List[str]]=Form([]),
        relation: Optional[str] = Form(None),
        at_least: Optional[int] = Form(0)
):
    return LoadPluginModel(tool_type=tool_type, num_trials=num_trials, print_to_cli=print_to_cli, gene_set_ids=gene_set_ids, relation=relation, at_least=at_least)

class TaskInstance:
    def __init__(self, instance,data):
        self.result = None
        self.lock = Lock()
        self.ats=instance
        self.data = data
        self.thread = Thread(target=self.run)
        self.thread.start()

    def run(self):
        self.result = asyncio.run(self.ats.execute(self.data))

    def get_status(self):
        with self.lock:
            return self.ats.get_status()

    def get_result(self):
        self.thread.join()
        with self.lock:
            return self.result


class TaskManager:
    def __init__(self):
        self.tasks = {}

    def create_task(self,instance, data) -> str:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = TaskInstance(instance,data)
        return task_id

    def get_status(self, task_id: str) -> str:
        task = self.tasks.get(task_id)
        if task:
            re=task.get_status()
            print(re)
            return re
        return "Invalid Task ID"

    def get_result(self, task_id: str):
        task = self.tasks.get(task_id)
        if task:
            return task.get_result()
        return "Invalid Task ID"


def constructInput(input,bgFile,upFiles):
    from collections import defaultdict
    dic=defaultdict(lambda:None)
    tools_yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools.yaml")
    with open(tools_yaml_path, "r") as file:
        config=yaml.safe_load(file)
    tool_type = input.tool_type
    reqInputs=config["tools_input"].get(tool_type)
    print(reqInputs)
    filePath="file_path_"
    geneids="geneset_id_"
    for items in reqInputs:
        if items=="background_file_path":
            dic[items]=bgFile[0] if len(bgFile)!=0 else None
        elif filePath in items or geneids in items:
            tt=items.split("_")
            if geneids in items:
                dic[items]=input.gene_set_ids[int(tt[-1])-1]  if len(input.gene_set_ids)>int(tt[-1])-1 else None
            else:
                dic[items]=upFiles[int(tt[-1])-1] if len(upFiles)>int(tt[-1])-1 else None
        elif items=="relation":
            dic[items]=input.relation
        elif items=="at_least":
            dic[items]=input.at_least
        else:
            dic[items]=input.dict().get(items)
    dic["tools_input"]=tool_type
    return dic


def constructInputNew(tool,dic):
    pass


task_manager = TaskManager()

@app.post("/load_plugin/")
async def load_plugin(input: LoadPluginModel=Depends(parse_metadata),files: Optional[List[UploadFile]] = File([]),bgFiles: Optional[List[UploadFile]] = File([])):
    try:
        upFiles,bgUpFiles=[],[]
        for ff in files:
            file_path = os.path.join(UPLOAD_DIR, ff.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(ff.file, buffer)
            upFiles.append(file_path)

        for ff in bgFiles:
            file_path = os.path.join(UPLOAD_DIR, ff.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(ff.file, buffer)
            bgUpFiles.append(file_path)

        # Retrieve plugin class instance
        imp_plugins = ATS_Plugin.implement_plugins()

        if imp_plugins:
            toolInput=constructInput(input,bgUpFiles,upFiles)
            task_id=task_manager.create_task(imp_plugins,toolInput)
        else:
            raise ValueError(f'Unknown plugin type:{input.get("tool_type")}')
    except Exception as e:
        print(e)
        return {"error": e}
    return {"task_id": task_id}

@app.get("/status/{task_id}")
def get_status(task_id: str):
    return {"task_id": task_id, "status": task_manager.get_status(task_id)}

@app.get("/result/{task_id}")
def get_result(task_id: str):
    result = task_manager.get_result(task_id)
    print(result)
    return {"task_id": task_id, "result": result}

with open("tools_new.yaml", "r") as f:
    tools_config = yaml.safe_load(f)

# Type map for form inputs
type_map = {
    "str": str,
    "int": int,
    "List<str>": List[str],
    "bool": bool,
    "UploadFile": UploadFile,
}

def make_endpoint(tool: str, params: list) -> Callable:
    # Create async handler
    async def endpoint_func(**kwargs):
        # inputt=constructInputNew(tool,dict(kwargs))
        for key,values in kwargs.items():
            print(key)
            if type(values)==starlette.datastructures.UploadFile:
                file_path = os.path.join(UPLOAD_DIR, values.filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(values.file, buffer)
                kwargs[key]=values.filename
        kwargs["tools_input"]=tool
        imp_plugins = ATS_Plugin.implement_plugins()
        if imp_plugins:
            task_id=task_manager.create_task(imp_plugins,kwargs)
        else:
            raise ValueError(f'Unknown plugin type:{tool}')
        return JSONResponse(content={"tool": tool, "received": kwargs,"task_id":task_id})

    # Build signature dynamically
    param_defs = {}
    for p in params:
        param_type = type_map.get(p["type"])
        default_value = File(None) if param_type == UploadFile else Form(None)
        param_defs[p["name"]] = inspect.Parameter(
            p["name"],
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=default_value,
            annotation=param_type,
        )

    # Set custom signature
    sig = inspect.Signature(parameters=list(param_defs.values()))
    endpoint_func.__signature__ = sig
    return endpoint_func

# Register endpoints
# for tools in tools_config["tools_input"]:
for tool_name, inputs in tools_config["tools_input"].items():
    endpoint = make_endpoint(tool_name, inputs)
    app.add_api_route(f"/{tool_name}", endpoint, methods=["POST"])