from random import randint as random_randint
from random import choice as random_choice
import crud
from psycopg2 import Error as psycopg2_Error
from faker import Faker
import config


fake = Faker('ru_RU')


def gen_users(update, _):
    # user_ids = [177381168, 990012649, 157218637]  # 157218637 - alex, 990012649 - Илья
    real_users_ids = [177381168, 157218637]  # 990012649
    bot_users_ids = [(1000 + user_id) for user_id in range(50)]
    all_users_ids = real_users_ids + bot_users_ids
    for user_id in all_users_ids:
        name, gender = (fake.unique.first_name_male(), 1) if fake.pybool() else (fake.unique.first_name_female(), 2)
        user_dict = {'name': name,
                     'goal': random_randint(1, 3),
                     'gender': gender,
                     'age': random_randint(10, 90),
                     'country': 'Russia',
                     'city': fake.city_name(),
                     'comment': 'bot' if user_id not in real_users_ids else None}
        try:
            photos = config.MEN_PHOTOS_FOR_GEN if user_dict['gender'] == 1 else config.WOMEN_PHOTOS_FOR_GEN
            crud.create_user(tg_user_id=user_id,
                             name=user_dict['name'],
                             goal=user_dict['goal'],
                             gender=user_dict['gender'],
                             age=user_dict['age'],
                             country=user_dict['country'],
                             city=user_dict['city'],
                             comment=user_dict['comment'],
                             photos=[random_choice(photos)])
        except psycopg2_Error:
            pass
    update.message.reply_text('ok')


def gen_posts(update, _):
    for i in range(20):
        crud.create_post(tg_user_id=update.effective_user.id, message_id=config.DEFAULT_POST_MESSAGE_ID)
    update.message.reply_text('ok')


def gen_likes(update, _):
    # users_id = crud.read_any(table='users',
    #                          select_columns='tg_user_id',
    #                          column='comment',
    #                          value='bot',
    #                          fetch='fetchall')
    users_id = crud.read_users()
    posts_id = crud.read_any(table='posts', select_columns='id', fetch='fetchall')
    for user_id in users_id:
        for message_id, post_id in enumerate(posts_id):
            crud.create_vote(tg_user_id=user_id, post_id=post_id, vote=random_randint(-1, 1), message_id=message_id)
    update.message.reply_text('ok')


def drop_all(update, _):
    crud.delete_any(table='posts')
    crud.delete_any(table='votes')
    crud.delete_any(table='users')
    update.message.reply_text('ok')


# noinspection PyUnusedLocal
def gen_all(update, context):
    gen_users(update, context)
    gen_posts(update, context)
    gen_likes(update, context)
