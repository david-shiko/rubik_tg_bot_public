import keyboards
import config
import postconfig
import crud
import sqls
from bot import bot
from telegram import ParseMode as tg_ParseMode
from telegram import InputMediaPhoto as tg_InputMediaPhoto


class User:

    def __init__(self, tg_user_id: int):
        self.connection = postconfig.global_connection
        self.cursor = self.connection.cursor()
        self.tg_user_id = tg_user_id
        self.tg_photos = crud.read_user_photos(tg_user_id=self.tg_user_id, cursor=self.cursor)
        if user_profile_text := crud.read_user_text_data(tg_user_id=self.tg_user_id, cursor=self.cursor):
            # List comprehension to convert float to int (produced because of birthdate calculation)
            profile_text = [int(i) if type(i) is float else i for i in user_profile_text]
            self.name, self.goal, self.gender, self.age, self.country, self.city, self.comment = profile_text
        else:
            self.name = self.goal = self.gender = self.age = self.country = self.city = self.comment = None

    def show_profile(self, show_to_id: int):
        caption = ''
        for key, value in self.translate_profile_text().items():
            caption += f'{key} - {value}.\n'
        photos = self.tg_photos or [config.DEFAULT_PHOTO]
        input_media_photos = photos.copy()  # input_media_photos -some TG feature
        for i, photo in enumerate(input_media_photos):  # iterate over copy of photos and replace them
            input_media_photos[i] = tg_InputMediaPhoto(media=photo, caption=caption, parse_mode=tg_ParseMode.HTML)
        bot.send_media_group(chat_id=show_to_id, media=input_media_photos)  # send group of photos
        if len(photos) > 1:  # If media_group contain only one photo TG sends it with explicitly caption
            bot.send_message(chat_id=show_to_id, text=caption, parse_mode=tg_ParseMode.HTML)  # send text caption

    def translate_profile_text(self) -> dict:
        translated_profile_data_with_str_none = {  # translate_profile_data
            'Имя': f"<a href='tg://user?id={self.tg_user_id}'>{self.name}</a>",  # add link with user to a message
            'Цель':
                'Хочет общаться' if self.goal == 1 else  # one of three options
                ('Хочет знакомиться' if self.goal == 2 else 'Общаться и знакомиться'),
            'Пол': 'Я парень' if self.gender == 1 else 'Я девушка',
            'Возраст': self.age,
            'Местоположение': f'{self.country}, {self.city}',
            'О себе': self.comment}
        # Value may has 'None' :str inside
        return {k: v for k, v in translated_profile_data_with_str_none.items() if str(None) not in str(v)}


class NewUser(User):

    def __init__(self, tg_user_id):
        super().__init__(tg_user_id)
        self.tg_photos = list()  # Empty list for photos (no inherit photos from parent class)
        self.current_keyboard = keyboards.original_photo_keyboard
        self.old_media_group_id = None  # For internal using as condition

    def create_user(self):
        crud.delete_user(tg_user_id=self.tg_user_id, cursor=self.cursor)  # First delete user if already exists
        crud.create_user(tg_user_id=self.tg_user_id,
                         name=self.name,
                         goal=self.goal,
                         gender=self.gender,
                         age=self.age or 0,  # age or 0 -to subtract age from current_date)
                         country=self.country,
                         city=self.city,
                         comment=self.comment,
                         photos=[self.tg_photos],
                         cursor=self.cursor)


class TargetUser(User):
    # covotes_count - all matches count, matches_count - filtered matches count
    checkboxes = {'age': 1, 'photo': 0, 'country': 0, 'city': 0}

    def __init__(self, tg_user_id: int):
        super().__init__(tg_user_id)
        self.tg_user_id = tg_user_id
        self.connection = postconfig.DBConnectionManager.get_connection()  # Override, create personal connection
        self.goal = self.gender = self.age_range = self.country = self.city = None
        self.cursor.execute(sqls.create_temp_table_my_votes, (self.tg_user_id,))
        self.cursor.execute(sqls.create_temp_table_my_covotes, (self.tg_user_id,))
        self.my_votes = crud.read_my_votes(cursor=self.cursor)
        self.current_matches = self.new_matches = crud.read_my_covotes(cursor=self.cursor)
        self.current_matches_count = len(self.current_matches)
        self.new_matches_count = len(self.new_matches)
        self.votes_count = len(self.my_votes)
        self.flag = False  # Just for user convenience

    def show_match(self):  # TODO show how many matches is rest
        if self.current_matches:
            matched_tg_user_id, common_interests_count = self.current_matches.pop()
            common_interests_perc = round(100 / (self.votes_count / common_interests_count))
            bot.send_message(chat_id=self.tg_user_id,
                             reply_markup=keyboards.keyboard_for_one_more_match,
                             text=f'Вам подходит:\n'
                                  f"Процент общих интересов: {common_interests_perc}%\n"
                                  f'Общих интересов: {common_interests_count}',)
            self.show_profile(show_to_id=self.tg_user_id)
            self.insert_shown_user(tg_shower_id=matched_tg_user_id)
        else:
            bot.send_message(chat_id=self.tg_user_id,
                             text='Отличная работа, вы посмотрели все совпадения! Завершаю диалог.',
                             reply_markup=keyboards.remove_keyboard())  # keyboards.keyboard_for_new_search
            return bot.end_conversation()

    def use_goal_filter(self) -> None:
        self.cursor.execute('DROP TABLE IF EXISTS users_filtered_by_goal')
        self.cursor.execute(sqls.use_goal_filter, (self.goal,))

    def use_gender_filter(self) -> None:
        self.cursor.execute('DROP TABLE IF EXISTS users_filtered_by_gender')
        self.cursor.execute(sqls.use_gender_filter, (self.gender,))  # For 'IN' operator need parentheses even for tuple

    def use_age_filter(self) -> None:
        self.cursor.execute('DROP TABLE IF EXISTS users_filtered_by_age')
        self.cursor.execute(sqls.use_age_filter, (self.age_range[1], self.age_range[0],))

    # def _create_temp_table_colikes_filtered_v2(self) -> None:
    #     """
    #     INTERSECT IN MUCH MORE FASTER THAT 'AND tg_user_id IN'
    #     but INTERSECT IS NOT SUPPORTING different columns count.
    #     So you can add second column to every 'users_filtered_by' table,
    #     but in this case this tables won't be able to use INTERSECT.
    #     So whether in 'colikes_filtered' INTERSECT whether in 'users_filtered_by'.
    #     """
    #     sql = f'''CREATE TEMPORARY TABLE colikes_filtered AS
    #     SELECT tg_user_id, count_common_interests FROM my_covotes
    #     INTERSECT (SELECT tg_user_id FROM users_filtered_by_goal)
    #     INTERSECT (SELECT tg_user_id FROM users_filtered_by_gender)
    #     INTERSECT (SELECT tg_user_id FROM users_filtered_by_age)
    #     {'INTERSECT (SELECT tg_user_id FROM users WHERE birthdate IS NOT NULL)' if self.checkboxes['age'] else ''}
    #     {'INTERSECT (SELECT tg_user_id FROM users WHERE country IS NOT NULL)' if self.checkboxes['country'] else ''}
    #     {'INTERSECT (SELECT tg_user_id FROM users WHERE city IS NOT NULL)' if self.checkboxes['city'] else ''}
    #     {'INTERSECT SELECT DISTINCT tg_user_id FROM photos' if self.checkboxes['photo'] else ''}
    #     GROUP BY tg_user_id ORDER BY count_common_interests ASC'''
    #     self.cursor.execute(sql)

    def set_matches(self, reset_checkboxes: bool = False):
        try:
            # Get list of values, along all values last values is count of column
            self.cursor.execute(sqls.create_temp_table_colikes_filtered) if not reset_checkboxes else None
            self.cursor.execute(sqls.create_temp_table_colikes_checkboxes(self.checkboxes))
            self.cursor.execute(sqls.select_all_matches)
            self.current_matches = self.cursor.fetchall()
            self.current_matches_count = len(self.current_matches)
            return self.current_matches
        except Exception as e:
            postconfig.logger.error(f'Error in set_all_matches, {e}')

    def set_new_matches(self) -> None:
        self.cursor.execute(sqls.select_new_matches, (self.tg_user_id,))
        self.new_matches = self.cursor.fetchall()
        self.new_matches_count = len(self.new_matches)

    def filter_users_by_show(self) -> None:
        self.cursor.execute(sqls.filter_users_by_show, self.tg_user_id)

    def insert_shown_user(self, tg_shower_id) -> None:
        # 'ON CONFLICT -Do nothing if key duplicate
        sql = 'INSERT INTO shown_users (tg_user_id, shown_id) VALUES (%s, %s) ON CONFLICT DO NOTHING'
        self.cursor.execute(sql, (self.tg_user_id, tg_shower_id,))


class MatchedUser(User):  # Not in user
    def __init__(self, tg_user_id):
        super().__init__(tg_user_id)


class Post:

    def __init__(self, post_id: int = None, caption: str = '', recipient: all or int = None) -> None:
        self.connection = postconfig.global_connection
        self.cursor = self.connection.cursor()
        self.post_id = None
        self.author = None
        self.post_message_id = None
        self.likes_count = None
        self.dislikes_count = None
        self.caption = caption
        self.default_caption = ('\n\nПоставьте "лайк" или "дизлайк" посту что-бы общаться с теми, '
                                'кто оценил его так-же как вы')
        self._set_post(post_id=post_id, recipient=recipient)  # Will be set if recipient or post id passed

    def _set_post(self, post_id: int, recipient: int, post_status: int = 0) -> tuple or None:
        if post_id:
            post = crud.read_post(post_id=post_id)
        elif recipient == all:
            self.cursor.execute(sqls.select_public_post, (post_status,))
            post = self.cursor.fetchone()
        elif type(recipient) == int:
            self.cursor.execute(sqls.select_personal_post, (post_status, recipient))
            post = self.cursor.fetchone()
        else:
            return
        self.post_id, self.author, self.post_message_id, self.likes_count, self.dislikes_count = post
        return post

    @staticmethod
    def create_post(tg_user_id, message_id):
        crud.create_post(tg_user_id, message_id)

    def set_vote(self, tg_user_id: int, post_id: int, new_vote: int) -> bool or int:
        old_vote = crud.read_vote(tg_user_id=tg_user_id, post_id=post_id)[0]
        old_vote = 0 if old_vote is None else old_vote
        if post := crud.read_post(post_id=post_id):  # If given post is exists a vote also exists;

            self.likes_count, self.dislikes_count = post[3], post[4]

            if old_vote == 0 and new_vote == 1:
                self.likes_count += 1
            elif old_vote == 0 and new_vote == -1:
                self.dislikes_count += 1
            elif old_vote == 1 and new_vote == -1:
                self.likes_count -= 1
            elif old_vote == -1 and new_vote == 1:
                self.dislikes_count -= 1
            else:
                return  # Callback data goes from user

            # TODO fix if no exists
            crud.update_vote(tg_user_id=tg_user_id, post_id=post_id, dict_={'vote': old_vote + new_vote})
            crud.update_post(dict_={'likes_count': self.likes_count, 'dislikes_count': self.dislikes_count},
                             post_id=post_id)
            return True
        else:
            return 1  # Such post isn't exists

    def save_shown_post(self, tg_user_id: int, post_message_id: int):
        """
        Link tg_message with post (for every user it's different)
        tg_message stored in votes (as it's also personal for every user)
        """
        crud.create_vote(tg_user_id=tg_user_id, post_id=self.post_id, message_id=post_message_id, vote=None)

    def update_release_time(self):
        crud.update_post(dict_={'release_time': ['CURRENT_TIMESTAMP']}, post_id=self.post_id)
