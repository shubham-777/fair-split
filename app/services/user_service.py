from app.models.user import User
from app.services.base_service import BaseService


class UserService(BaseService):
    
    def get_by_email(self, email: str) -> User:
        return self.session.query(User).filter(User.email == email).first()
