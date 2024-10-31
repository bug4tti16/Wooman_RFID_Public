from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from os.path import join

files=StaticFiles(directory=join(Path(__file__).parent,"routes"))
filerouter=APIRouter()

@filerouter.get("/tag")
def main():
    return RedirectResponse(url="tag/index.html")