from typing import Optional
from enum import Enum

from models.core import DateTimeModelMixin, IDModelMixin, CoreModel


class NewsStatus(str, Enum):
    new = "new"
    partially_completed = "partially_completed"
    completed = "completed"
    published = "published"
    deleted = "deleted"


class NewsBase(CoreModel):
    text: Optional[str]
    image: Optional[str]
    video: Optional[str]
    author: Optional[str]
    message_id: Optional[str]
    status: Optional[NewsStatus] = NewsStatus.new


class NewsCreate(CoreModel):
    """
    The only field required to create a news is the users id
    """
    user_id: int
    status: Optional[NewsStatus] = NewsStatus.new


class NewsUpdate(NewsBase):
    pass


class NewsInDB(IDModelMixin, DateTimeModelMixin, NewsBase):
    user_id: int


class NewsPublic(NewsInDB):
    pass
