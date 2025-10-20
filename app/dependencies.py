from typing import Annotated, TypeAlias

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import engine


def get_session():
    with Session(engine) as session:
        yield session
        
    
SessionDep: TypeAlias = Annotated[Session, Depends(get_session)]
