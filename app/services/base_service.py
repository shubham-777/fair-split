from sqlalchemy.orm import Session

from app.dependencies import get_session, SessionDep
from app.models.user import User
from app.schemas.users import ReadUser


class BaseService:
    
    def __init__(self, session: Session = None, current_user: User = None):
        if not session:
            self.session = get_session()
        else:
            self.session = session
            
        self.user = current_user
    
    def add(self, obj):
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj
    
    def update(self, obj):
        self.session.merge(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj
    
    def delete(self, obj):
        self.session.delete(obj)
        self.session.flush()
    
    def get(self, model, id):
        return self.session.get(model, id)
    
    def commit(self):
        self.session.commit()
    
    def rollback(self):
        self.session.rollback()
    
    def close(self):
        self.session.close()
    
    def add_and_commit(self, obj):
        obj = self.add(obj)
        self.commit()
        return obj
    
    def delete_and_commit(self, obj):
        self.delete(obj)
        self.commit()
        return obj
    
    def update_and_commit(self, obj):
        obj = self.update(obj)
        self.commit()
        return obj
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()