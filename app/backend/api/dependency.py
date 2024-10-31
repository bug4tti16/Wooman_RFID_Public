from collections.abc import Generator
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends


from backend.database import database,User

def get_db() -> Generator[Session, None, None]:
    with database._session("new") as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

