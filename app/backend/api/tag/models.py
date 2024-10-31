from datetime import date
from pydantic import BaseModel
from typing import Union, Literal, List

from backend.database import User, Log


class TagResponse(BaseModel):
    num: str
    name: str
    time: str
    menu: str
    exists: int | None
    @classmethod
    def _form(cls,user_obj:User,exists:Literal["New","Exists"]=None):
        name=user_obj.name
        num=str(user_obj.card_number)
        time="금일 미이용"
        menu=""
        exist=None
        if exists:
            exist=1 if exists=="Exists" else 0
        if user_obj.use:
            use=user_obj.use[-1]
            if(use.canceled):
                pass
            else:
                time=use.timestamp.strftime("%H시 %M분")
                menu=use="죽식" if use.menu else ""
        return cls(num=num,name=name,time=time,menu=menu,exists=exist)
    


class AutocorrectResponse(BaseModel):
    result: List[TagResponse]

    @classmethod
    def _form(cls,user_list:list[User]):
        
        if user_list:
            l=[]
            for user_obj in user_list[:10]:
                l.append(TagResponse._form(user_obj))
            cls.result=l
            return cls
        else:
            cls.result=[]
            return cls
        
    @classmethod
    def _load(cls,user_list:list[User]):
        if user_list:
            l=[]
            for user_obj in user_list:
                l.append(TagResponse._form(user_obj))
            cls.result=l
            return cls
        else:
            cls.result=[]
            return cls
        
class CountResponse(BaseModel):
    total:str
    menu:str