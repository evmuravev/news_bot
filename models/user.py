from typing import Optional

from models.core import DateTimeModelMixin, IDModelMixin, CoreModel


class UserBase(CoreModel):
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    language_code: str
    is_bot: bool
    is_premium: Optional[bool]
    is_banned: Optional[bool] = False
    num_of_complains: Optional[int] = 0


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserInDB(DateTimeModelMixin, UserBase):
    pass


class UserPublic(IDModelMixin, DateTimeModelMixin, UserBase):
    pass
