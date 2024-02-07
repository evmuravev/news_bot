from databases import Database

from db.repositories.base import BaseRepository
from db.repositories.news import NewsRepository
from models.user import UserCreate, UserPublic, UserInDB, UserUpdate


GET_USER_BY_ID = """
    SELECT *
    FROM users
    WHERE id = :id;
"""

REGISTER_NEW_USER_QUERY = """
    INSERT INTO users (
        id,
        first_name,
        last_name,
        username,
        language_code,
        is_bot,
        link,
        is_premium,
        is_admin,
        is_banned,
        num_of_complains
    )
    VALUES (
        :id,
        :first_name,
        :last_name,
        :username,
        :language_code,
        :is_bot,
        :link,
        :is_premium,
        :is_admin,
        :is_banned,
        :num_of_complains
    )
    RETURNING *;
"""

UPDATE_USERNAME_QUERY = """
    UPDATE users
    SET username = :username
    WHERE id = :user_id
    RETURNING *;
"""

UPDATE_IS_BANNED_QUERY = """
    UPDATE users
    SET is_banned = :is_banned
    WHERE id = :user_id
    RETURNING *;
"""

UPDATE_NUM_OF_COMPLAINS_QUERY = """
    UPDATE users
    SET num_of_complains = num_of_complains + 1
    WHERE id = :user_id
    RETURNING *;
"""


class UsersRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.news_repo = NewsRepository(db)

    async def get_user_by_id(self, *,
                             id: int, populate: bool = True) -> UserPublic:
        user_record = await self.db.fetch_one(
            query=GET_USER_BY_ID, values={"id": id}
        )

        if user_record:
            user = UserInDB(**user_record)
            return user

    async def register_new_user(self, *, new_user: UserCreate) -> UserPublic:
        user = await self.db.fetch_one(
            query=REGISTER_NEW_USER_QUERY,
            values=new_user.dict()
        )
        return UserInDB(**user)

    async def update_is_banned(self, *, user_id: int) -> UserInDB:
        updated_user = await self.db.fetch_one(
            query=UPDATE_IS_BANNED_QUERY,
            values={"user_id": user_id, "is_banned": True},
        )

        return UserInDB(**updated_user)

    async def inc_num_of_complains(self, *, user_id: int) -> UserInDB:
        updated_user = await self.db.fetch_one(
            query=UPDATE_NUM_OF_COMPLAINS_QUERY,
            values={"user_id": user_id},
        )

        return UserInDB(**updated_user)
