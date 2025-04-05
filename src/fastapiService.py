import asyncio
import importlib
import os,shutil
from typing import Literal, Optional, List
from threading import Thread, Lock
import time
import uuid

import yaml
from fastapi import FastAPI, UploadFile, File, Form, Depends

from pydantic import BaseModel, Field


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
        gene_set_ids: Optional[List[str]]=Form([])
):
    return LoadPluginModel(tool_type=tool_type, num_trials=num_trials, print_to_cli=print_to_cli, gene_set_ids=gene_set_ids)

class TaskInstance:
    def __init__(self, instance,data):
        self.result = None
        self.lock = Lock()
        self.instance=instance
        self.data = data
        self.thread = Thread(target=self.run)
        self.thread.start()

    def run(self):
        self.result = asyncio.run(self.instance.run(self.data))

    def get_status(self):
        if self.thread.is_alive():
            return {"status": "still processing"}
        with self.lock:
            return self.instance.status()

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


task_manager = TaskManager()
#
# @app.post("/")
# def read_root(input:LoadPluginModel):
#     return {"Hello": "World"}


@app.post("/load_plugin/")
async def load_plugin(input: LoadPluginModel=Depends(parse_metadata),files: Optional[List[UploadFile]] = File([]),bgFiles: Optional[List[UploadFile]] = File([])):
    try:
        upFiles,bgUpFiles=[],[]
        geneIds = input.gene_set_ids
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


        tools_yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools.yaml")
        with open(tools_yaml_path, "r") as file:
            config=yaml.safe_load(file)
        tool_type = input.tool_type
        className=config["tools"].get(tool_type)
        print(className)
        if className:
            module_path, class_name = className.rsplit(".", 1)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            print(cls)
            if cls:
                print(bgUpFiles)
                print(upFiles)
                instance = cls()
                file_1=upFiles[0] if len(upFiles)>=2 else None
                file_2=upFiles[1] if len(upFiles)>=2 else None
                bg_file=bgUpFiles[0] if len(bgUpFiles)>=1 else None
                geneset_id_1= geneIds[0] if len(geneIds)>=1 else None
                geneset_id_2= geneIds[1] if len(geneIds)>=1 else None
                toolInput={"num_trials":input.num_trials,
                           "print_to_cli":input.print_to_cli,
                           "file_path_1":file_1,
                           "file_path_2":file_2,
                           "background_file_path":bg_file,
                           "geneset_id_1":geneset_id_1,
                           "geneset_id_2": geneset_id_2}
                task_id=task_manager.create_task(instance,toolInput)
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