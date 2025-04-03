import asyncio
import importlib
import os,shutil
from typing import Union, Literal, Optional, List

import yaml
from fastapi import FastAPI, UploadFile, File, Form, Depends

from pydantic import BaseModel, Field


class LoadPluginModel(BaseModel):
    tool_type: Literal["MSET","Boolean"]
    num_trials: Optional[int]= 1000
    print_to_cli: Optional[bool]= True

UPLOAD_DIR = os.getcwd()

app = FastAPI()

class FileMetadata(BaseModel):
    title: str
    description: str

# Function to extract metadata from form fields
def parse_metadata(
        tool_type: str = Form(...),
        num_trials: int = Form(...),
        print_to_cli: bool=Form(...)
):
    return LoadPluginModel(tool_type=tool_type, num_trials=num_trials, print_to_cli=print_to_cli)

# @app.post("/upload/")
# async def upload_file(
#         file: UploadFile = File(...),
#         metadata: FileMetadata = Depends(parse_metadata)
# ):
#     return {
#         "filename": file.filename,
#         "content_type": file.content_type,
#         "metadata": metadata.dict()
#     }


@app.post("/")
def read_root(input:LoadPluginModel):
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/load_plugin/")
async def load_plugin(input: LoadPluginModel=Depends(parse_metadata),files: List[UploadFile] = File(...),bgFiles: List[UploadFile] = File(...)):
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
        tools_yaml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools.yaml")
        with open(tools_yaml_path, "r") as file:
            config=yaml.safe_load(file)
        tool_type = input.tool_type
        className=config["tools"].get(tool_type) # "tool type" in input dictionary determines tool selection
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
                toolInput={"num_trials":input.num_trials,"print_to_cli":input.print_to_cli,"file_path_1":upFiles[0],"file_path_2":upFiles[1],"background_file_path":bgUpFiles[0]}
                print("Before")
                result = await instance.run(toolInput)
                print(result)
        else:
            raise ValueError(f'Unknown plugin type:{input.get("tool_type")}')
    except Exception as e:
        print(e)
        return {"error": e}