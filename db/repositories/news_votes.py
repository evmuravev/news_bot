from typing import List
from databases import Database
from db.repositories.base import BaseRepository
from db.repositories.news import NewsRepository
from models.news_votes import NewsVotesCreate, NewsVotesInDB, NewsVotesUpdate


CREATE_NEWS_VOTES = """
    INSERT INTO news_votes (news_id, pros, cons)
    VALUES (:news_id, :pros, :cons)
    RETURNING *;
"""

GET_NEW_COMPLAIN = """
    SELECT *
    FROM complains
    WHERE complainant = :complainant
        AND accused = :accused
        AND status = 'new'
    ;
"""

UPDATE_COMPLAIN_STATUS = """
    UPDATE complains
    SET status = :status
    WHERE id = :id
    RETURNING *;
"""

GET_ALL_COMPLAINS_QUERY = """
    SELECT *
    FROM complains
    WHERE accused = :accused
        AND status = 'new'
    ;
"""


class NewsVotesRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.profiles_repo = NewsRepository(db)

    async def create_news_votes(
            self, *,
            news_votes_create: NewsVotesCreate
    ) -> NewsVotesInDB:

        news_votes = await self.db.fetch_one(
            query=CREATE_NEWS_VOTES,
            values=news_votes_create.dict()
        )

        return NewsVotesInDB(**news_votes)

    async def get_complain(
            self, *,
            complainant_id: int,
            accused_id: int,
    ) -> NewsVotesInDB:
        complain = await self.db.fetch_one(
            query=GET_NEW_COMPLAIN,
            values={
                "complainant": complainant_id,
                "accused": accused_id
            }
        )
        if complain:
            return NewsVotesInDB(**complain)

    async def update_status_complain(
            self, *,
            complain_update: NewsVotesUpdate,
    ) -> NewsVotesInDB:
        complain = await self.db.fetch_one(
            query=UPDATE_COMPLAIN_STATUS,
            values={
                "id": complain_update.id,
                "status": complain_update.status
            }
        )
        return NewsVotesInDB(**complain)

    async def get_all_complains(
            self, *,
            accused_id: int,
    ) -> List[NewsVotesInDB]:
        complains = await self.db.fetch_all(
            query=GET_ALL_COMPLAINS_QUERY,
            values={
                "accused": accused_id,
            }
        )
        if complains:
            return [NewsVotesInDB(**complain) for complain in complains]
