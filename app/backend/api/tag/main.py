from fastapi import APIRouter,HTTPException
from fastapi.responses import HTMLResponse
from typing import Union


from backend.api.dependency import SessionDep
from backend.database import Search, TagMethod
from .models import AutocorrectResponse, TagResponse,CountResponse


tagrouter=APIRouter(prefix="/tag/api")




@tagrouter.get(path="/search",response_model=AutocorrectResponse,status_code=200)
def get_kw(session:SessionDep,kw:Union[str,None]=None):
    if kw:
        return AutocorrectResponse._form(Search._kw(session=session,kw=kw))
    raise HTTPException(status_code=404,detail="No result found")


@tagrouter.get(path="/",response_model=TagResponse,status_code=201)
def tag_in(session:SessionDep,data:Union[str,None]=None):
    if data:
        user_obj=TagMethod._tag_user(session=session,data=data)
        if not user_obj:
            raise HTTPException(status_code=404)
        return TagResponse._form(user_obj=user_obj[0],exists=user_obj[1])

@tagrouter.get("/init",response_model=AutocorrectResponse,status_code=200)
def load(session:SessionDep):
    return AutocorrectResponse._load(user_list=Search._load(session=session))


@tagrouter.get("/menu",response_model=TagResponse,status_code=201)
def menu_ch(session:SessionDep,data:Union[str,None]=None):
    if data:
        user_obj=TagMethod._menu(session=session,data=data)
        if not user_obj:
            raise HTTPException(status_code=400)
        return TagResponse._form(user_obj)
    raise HTTPException(status_code=400)

@tagrouter.get("/cancel",response_model=TagResponse,status_code=201)
def cancel_user(session:SessionDep,data:Union[str,None]=None):
    if data:
        user_obj=TagMethod._cancel(session=session,data=data)
        if not user_obj:
            raise HTTPException(status_code=400)
        return TagResponse._form(user_obj)
    raise HTTPException(status_code=400)

@tagrouter.get("/count",response_model=CountResponse,status_code=200)
def cnt(session:SessionDep):
    res=Search._count(session=session)
    if res:
        return CountResponse(total=str(res[1]),menu=str(res[0]))