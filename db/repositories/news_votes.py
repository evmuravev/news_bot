from typing import List
from databases import Database
from databases.interfaces import Record
from db.repositories.base import BaseRepository
from db.repositories.news import NewsRepository
from models.news_votes import NewsVotesCreate, NewsVotesInDB, NewsVotesUpdate


CREATE_NEWS_VOTES = """
    INSERT INTO news_votes (news_id, user_id, pros, cons)
    VALUES (:news_id, :user_id, :pros, :cons)
    RETURNING *;
"""

GET_NEWS_VOTES_BY_USER_ID = """
    SELECT *
    FROM news_votes
    WHERE news_id = :news_id
        AND user_id = :user_id;
"""

UPDATE_NEWS_VOTES = '''
    UPDATE news_votes
    SET
        news_id  = :news_id,
        user_id  = :user_id,
        pros     = :pros,
        cons     = :cons
    WHERE
        news_id = :news_id
        AND user_id = :user_id
    RETURNING *;
'''

GET_RATING = '''
    SELECT SUM(pros) - SUM(cons) as rating
    FROM news_votes
    WHERE news_id = :news_id
'''


class NewsVotesRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.profiles_repo = NewsRepository(db)

    async def create_news_votes(
            self, *,
            news_votes_create: NewsVotesCreate
    ) -> Record:

        news_votes = await self.db.fetch_one(
            query=CREATE_NEWS_VOTES,
            values=news_votes_create.dict()
        )

        return news_votes

    async def get_news_votes(
            self, *,
            news_id: int,
            user_id: int,
    ) -> NewsVotesInDB:
        news_votes_record = await self.db.fetch_one(
            query=GET_NEWS_VOTES_BY_USER_ID,
            values={
                "news_id": news_id,
                "user_id": user_id,
            }
        )
        if not news_votes_record:
            news_votes_create = NewsVotesCreate(
                news_id=news_id,
                user_id=user_id,
            )
            news_votes_record = await self.create_news_votes(
                news_votes_create=news_votes_create
            )

        return NewsVotesInDB(**news_votes_record)

    async def news_upvote(self, *, news_id: int, user_id: int) -> int:
        news_votes = await self.get_news_votes(
            news_id=news_id,
            user_id=user_id
        )
        update_params = news_votes.copy(
            update={"pros": 1, "cons": 0}
        )
        await self.db.fetch_one(
            query=UPDATE_NEWS_VOTES,
            values=update_params.dict(
                exclude={"created_at", "updated_at"}
            ),
        )
        rating = await self.db.fetch_one(
            query=GET_RATING,
            values={"news_id": news_id}
        )
        return rating['rating']

    async def news_downvote(self, *, news_id: int, user_id: int) -> int:
        news_votes = await self.get_news_votes(
            news_id=news_id,
            user_id=user_id
        )
        update_params = news_votes.copy(
            update={"pros": 0, "cons": 1}
        )
        await self.db.fetch_one(
            query=UPDATE_NEWS_VOTES,
            values=update_params.dict(
                exclude={"created_at", "updated_at"}
            ),
        )
        rating = await self.db.fetch_one(
            query=GET_RATING,
            values={"news_id": news_id}
        )
        return rating['rating']