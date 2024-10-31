from fastapi import FastAPI
import uvicorn
import locale

from backend.api.tag import tagrouter
from backend.database.porting import TransferData
from frontend.main import files, filerouter

locale.setlocale(locale.LC_ALL, 'kor')
app=FastAPI()
app.include_router(router=tagrouter)
app.include_router(router=filerouter)
app.mount("/",files)

port=TransferData()

if __name__=="__main__":
    uvicorn.run(app)
