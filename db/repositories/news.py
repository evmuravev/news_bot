from db.repositories.base import BaseRepository
from models.news import NewsCreate, NewsUpdate, NewsInDB


CREATE_NEWS_FOR_USER_QUERY = """
    INSERT INTO news (user_id, status)
    VALUES (:user_id, :status)
    RETURNING *;
"""

GET_LAST_NEWS_BY_USER_ID_QUERY = """
    SELECT *
    FROM news
    WHERE user_id = :user_id
        AND (status != 'published' AND status != 'deleted')
    ORDER BY _updated_at DESC
    LIMIT 1;
"""

GET_NEWS_BY_ID_QUERY = """
    SELECT *
    FROM news
    WHERE id = :id
        AND status != 'deleted';
"""


UPDATE_NEWS_QUERY = '''
    UPDATE news
    SET
        id          = :id,
        "text"      = :text,
        image       = :image,
        video       = :video,
        author      = :author,
        user_id     = :user_id,
        message_id  = :message_id,
        status      = :status
    WHERE
        id = :id
        AND  status != 'deleted'
    RETURNING *;
'''


class NewsRepository(BaseRepository):
    async def create_news(
            self, *,
            news_create: NewsCreate
    ) -> NewsInDB:

        created_news = await self.db.fetch_one(
            query=CREATE_NEWS_FOR_USER_QUERY,
            values=news_create.dict()
        )

        return created_news

    async def get_last_news_by_user_id(self, *, user_id: int) -> NewsInDB:
        news_record = await self.db.fetch_one(
            query=GET_LAST_NEWS_BY_USER_ID_QUERY,
            values={"user_id": user_id}
        )

        if news_record:
            return NewsInDB(**news_record)

    async def get_news_by_id(self, *, id: int) -> NewsInDB:
        news_record = await self.db.fetch_one(
            query=GET_NEWS_BY_ID_QUERY,
            values={"id": id}
        )

        if news_record:
            return NewsInDB(**news_record)

    async def update_news(
        self, *,
        news_update: NewsUpdate,
        news_id: int,
        exclude_unset=True
    ) -> NewsInDB:
        news = await self.get_news_by_id(id=news_id)
        update_params = news.copy(
            update=news_update.dict(exclude_unset=exclude_unset)
        )

        updated_news = await self.db.fetch_one(
            query=UPDATE_NEWS_QUERY,
            values=update_params.dict(
                exclude={"created_at", "updated_at"}
            ),
        )

        return NewsInDB(**updated_news)
