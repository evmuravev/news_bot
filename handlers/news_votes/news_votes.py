# import logging
# import random
# from telegram import (
#     InlineKeyboardButton,
#     InlineKeyboardMarkup,
#     Update,
# )
# from telegram.error import BadRequest
# from telegram.ext import (
#     ContextTypes,
# )
# from core.config import TELEGRAM_CHANNEL_ID
# from db.repositories.news_votes import ComplainRepository
# from db.repositories.news import NewsRepository
# from db.repositories.users import UsersRepository
# from db.tasks import get_repository

# from handlers.common.users import get_user

# from handlers.show_news.show_news import get_profile_description

# from models.user import UserPublic
# from utils.utils import escape_markdownv2


# logger = logging.getLogger()


# async def date_complain(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user: UserPublic = await get_user(update, context)

#     if user and user.is_banned:
#         await context.bot.answer_callback_query(
#             callback_query_id=update.callback_query.id,
#             show_alert=True,
#             text='Вы были забанены и больше не можете совершать действия!',
#         )
#         return

#     if not user or not user.profile:
#         await context.bot.answer_callback_query(
#             callback_query_id=update.callback_query.id,
#             show_alert=True,
#             text='Вы еще не создали профиль!\nПерейдите в бот для создания',
#         )
#         return

#     # Отправка жалобы
#     profile_repo: NewsRepository = get_repository(NewsRepository, context)
#     complains_repo = get_repository(ComplainRepository, context)

#     complainant = await profile_repo.get_last_news_by_user_id(
#         user_id=update.effective_user.id
#     )
#     accused = await profile_repo.get_news_by_id(
#         id=int(update.callback_query.data.split(':')[1])
#     )

#     complain = await complains_repo.get_complain(
#         complainant_id=complainant.id,
#         accused_id=accused.id,
#     )
#     if complain:
#         await context.bot.answer_callback_query(
#             callback_query_id=update.callback_query.id,
#             show_alert=True,
#             text='Ваша жалоба уже доставлена! Администраторы разбираются!',
#         )
#     else:
#         user_repo: UsersRepository = get_repository(UsersRepository, context)
#         accused_user = await user_repo.get_user_by_id(id=accused.user_id)

#         date_offer_repo = get_repository(DateOffersRepository, context)
#         date_offer: DateOfferPublic = await date_offer_repo.get_last_date_offer_by_profile_id(
#             profile_id=accused_user.profile.id
#         )
#         profile = await get_profile_description(accused_user.profile)
#         date_offfer_description = await get_date_offer_description(date_offer)
#         caption = profile.caption + date_offfer_description
#         image = await context.bot.get_file(profile.image)

#         options = [
#             [
#                 InlineKeyboardButton(
#                     "✔️ Все в порядке!",
#                     callback_data=f'date_complain_decline:{str(accused.id)}:{str(complainant.id)}'
#                 ),
#                 InlineKeyboardButton(
#                     "❌ Удалить свидание!",
#                     callback_data=f'date_complain_approve:{str(accused.id)}:{str(complainant.id)}'
#                 ),
#             ],
#             [InlineKeyboardButton(
#                 "❌ Удалить свидание и профиль!",
#                 callback_data=f'date_profile_complain_approve:{str(accused.id)}:{str(complainant.id)}'
#             )]
#         ]
#         keyboard = [*options]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         await context.bot.send_photo(
#                 chat_id=TELEGRAM_ADMIN_GROUP_ID,
#                 photo=image.file_id,
#                 caption=caption,
#                 parse_mode="MarkdownV2",
#                 reply_to_message_id=COMPLAIN_TOPIC_ID,
#                 reply_markup=reply_markup
#         )

#         # Запись жалобы в базу
#         complain_create = ComplainCreate(
#             complainant=complainant.id,
#             accused=accused.id,
#             message_id=date_offer.message_id
#         )
#         await complains_repo.create_complain(complain_create=complain_create)

#         # Связь с админом
#         selected_admin = random.choice(ADMINS)
#         options = [
#             [
#                 InlineKeyboardButton("✨ Связаться с администратором", url=f'https://t.me/{selected_admin}'),
#             ]
#         ]
#         keyboard = [*options]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         await context.bot.send_message(
#             chat_id=user.id,
#             text=f'Любые подробности по жалобе на "{escape_markdownv2(accused.name)}, {accused.age} лет, {escape_markdownv2(accused.city)}" Вы можете написать админиcтратору\!',
#             reply_markup=reply_markup,
#             parse_mode="MarkdownV2",
#         )

#         await context.bot.answer_callback_query(
#             callback_query_id=update.callback_query.id,
#             show_alert=True,
#             text='Ваша жалоба доставлена администраторам! Скоро они со всем разберутся 🫡',
#         )


# async def news_decline(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     profile_repo: NewsRepository = get_repository(NewsRepository, context)
#     accused_id = update.callback_query.data.split(':')[1]
#     complainant_id = update.callback_query.data.split(':')[2]
#     complainant_profile = await profile_repo.get_news_by_id(
#         id=int(complainant_id)
#     )
#     accused_profile = await profile_repo.get_news_by_id(
#         id=int(accused_id)
#     )
#     await context.bot.send_message(
#         chat_id=complainant_profile.user_id,
#         text=f'Ваша жалоба на свидание "{accused_profile.name}, {accused_profile.age} лет, {accused_profile.city}" \
# была рассмотрена, но ничего предосудительного мы не обнаружили! \
# Спасибо за бдительность!',
#     )

#     # Закрываем жалобу - меням статус в БД
#     complains_repo: ComplainRepository = get_repository(ComplainRepository, context)
#     complain = await complains_repo.get_complain(
#         complainant_id=int(complainant_id),
#         accused_id=int(accused_id),
#     )
#     if complain:
#         complain_update = complain.copy(update={'status': ComplainStatus.declined})
#         await complains_repo.update_status_complain(complain_update=complain_update)

#     # Удаляем сообщение из админской группы
#     try:
#         await context.bot.delete_message(
#             chat_id=TELEGRAM_ADMIN_GROUP_ID,
#             message_id=update.effective_message.message_id
#         )
#     except BadRequest as ex:
#         logger.warning(ex)


# async def news_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     profile_repo: NewsRepository = get_repository(NewsRepository, context)
#     accused_id = update.callback_query.data.split(':')[1]
#     accused_profile = await profile_repo.get_news_by_id(
#         id=int(accused_id)
#     )
#     # Удаляем свидание
#     date_offer_repo = get_repository(DateOffersRepository, context)
#     date_offer: DateOfferPublic = await date_offer_repo.get_last_date_offer_by_profile_id(
#         profile_id=accused_profile.id
#     )
#     if date_offer and date_offer.message_id is not None:
#         # delete the last message
#         try:
#             await context.bot.delete_message(
#                 chat_id=TELEGRAM_GROUP_ID,
#                 message_id=date_offer.message_id
#             )
#         except BadRequest as ex:
#             logger.warning(ex)

#         date_offer_update = {
#             'message_id': None
#         }
#         await date_offer_repo.update_date_offer(
#             date_offer_update=DateOfferUpdate(**date_offer_update),
#             profile_id=accused_profile.id
#         )

#         # Обвиняемому выписываем нарушение
#         user_repo = get_repository(UsersRepository, context)
#         user = await user_repo.get_user_by_id(id=accused_profile.user_id)
#         updated_user = await user_repo.inc_num_of_complains(user=user)
#         # Если больше 1, то в бан!
#         if updated_user.num_of_complains > 1:
#             await user_repo.update_is_banned(user=updated_user)
#             await context.bot.send_message(
#                 chat_id=accused_profile.user_id,
#                 text='Нам очень жаль, за повторное нарушение вы были забанены!',
#             )
#         else:
#             await context.bot.send_message(
#                 chat_id=accused_profile.user_id,
#                 text='За неподобающее содержание Ваше свидание было удалено! Повторное нарушение приведет вас к бану!',
#             )

#         # Отвечаем обвинителям
#         complains_repo: ComplainRepository = get_repository(ComplainRepository, context)
#         all_complains = await complains_repo.get_all_complains(accused_id=accused_profile.id)
#         for complain in all_complains:
#             complainant_profile = await profile_repo.get_news_by_id(
#                 id=complain.complainant
#             )
#             await context.bot.send_message(
#                 chat_id=complainant_profile.user_id,
#                 text=f'Ваша жалоба на свидание от "{accused_profile.name}, {accused_profile.age} лет, {accused_profile.city}" \
#         была рассмотрена - нарушитель наказан! \
#         Спасибо за бдительность!',
#             )

#             # Закрываем жалобу - меням статус в БД
#             complain_update = complain.copy(update={'status': ComplainStatus.approved})
#             await complains_repo.update_status_complain(complain_update=complain_update)

#     # Удаляем сообщение из админской группы
#     try:
#         await context.bot.delete_message(
#             chat_id=TELEGRAM_ADMIN_GROUP_ID,
#             message_id=update.effective_message.message_id
#         )
#     except BadRequest as ex:
#         logger.warning(ex)


# async def date_profile_complain_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     profile_repo: NewsRepository = get_repository(NewsRepository, context)
#     accused_id = update.callback_query.data.split(':')[1]
#     accused_profile = await profile_repo.get_news_by_id(
#         id=int(accused_id)
#     )
#     if accused_profile:
#         # Удаляем профиль и свидания
#         user_repo: UsersRepository = get_repository(UsersRepository, context)
#         user = await user_repo.get_user_by_id(id=accused_profile.user_id)
#         await delete_profile_and_dates(user, context)

#         # Обвиняемому выписываем нарушение
#         updated_user = await user_repo.inc_num_of_complains(user=user)
#         # Если больше 1, то в бан!
#         if updated_user.num_of_complains > 1:
#             await user_repo.update_is_banned(user=updated_user)
#             await context.bot.send_message(
#                 chat_id=accused_profile.user_id,
#                 text='Нам очень жаль, за повторное нарушение вы были забанены!',
#             )
#         else:
#             await context.bot.send_message(
#                 chat_id=accused_profile.user_id,
#                 text='За неподобающее содержание Ваше свидание и профиль были удалены! Повторное нарушение приведет вас к бану!',
#             )

#         # Отвечаем обвинителям
#         complains_repo: ComplainRepository = get_repository(ComplainRepository, context)
#         all_complains = await complains_repo.get_all_complains(accused_id=int(accused_id))
#         for complain in all_complains:
#             complainant_profile = await profile_repo.get_news_by_id(
#                 id=complain.complainant
#             )
#             await context.bot.send_message(
#                 chat_id=complainant_profile.user_id,
#                 text=f'Ваша жалоба на профиль "{accused_profile.name}, {accused_profile.age} лет, {accused_profile.city}" \
#         была рассмотрена - нарушитель наказан! \
#         Спасибо за бдительность! 🫡',
#             )

#             # Закрываем жалобу - меням статус в БД
#             complain_update = complain.copy(update={'status': ComplainStatus.approved})
#             await complains_repo.update_status_complain(complain_update=complain_update)

#     # Удаляем сообщение из админской группы
#     try:
#         await context.bot.delete_message(
#             chat_id=TELEGRAM_ADMIN_GROUP_ID,
#             message_id=update.effective_message.message_id
#         )
#     except BadRequest as ex:
#         logger.warning(ex)
