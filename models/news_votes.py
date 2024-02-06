from models.core import DateTimeModelMixin, CoreModel


class NewsVotesBase(CoreModel):
    news_id: int
    pros: int = 0
    cons: int = 0


class NewsVotesCreate(NewsVotesBase):
    pass


class NewsVotesUpdate(NewsVotesBase):
    pass


class NewsVotesInDB(DateTimeModelMixin, NewsVotesBase):
    pass


class NewsVotesPublic(NewsVotesInDB):
    pass
