from fastapi import HTTPException
from pydantic import EmailStr
from starlette import status

from app.models.user import User
from app.services.base_service import BaseService
from app.utils.security import hash_password, verify_password


class UserService(BaseService):
    
    def get_by_email(self, email: str | EmailStr) -> User:
        return self.session.query(User).filter(User.email == email).first()
    
    def get_if_active(self, email: str) -> User | None:
        user = self.get_by_email(email=email)
        if user and user.is_active:
            return user
        return None
    
    def update_password(self, user: User, new_password: str) -> User:
        user.hashed_password = hash_password(new_password)
        return self.update_and_commit(user)
    