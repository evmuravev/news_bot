from models.user import UserCreate, UserPublic
from db.repositories.users import UsersRepository
from db.tasks import get_repository
from telegram import Update
from telegram.ext import ContextTypes


async def register_new_user(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> UserPublic:
    new_user = UserCreate(**update.effective_user._get_attrs())
    user_repo = get_repository(UsersRepository, context)
    created_user = await user_repo.register_new_user(new_user=new_user)

    return created_user


async def get_user(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> UserPublic:
    user_repo = get_repository(UsersRepository, context)
    user = await user_repo.get_user_by_id(id=update.effective_user.id)
    return user
