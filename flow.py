import crud
import classes
import keyboards
import config
from bot import bot
from postconfig import logger
from locator import get_location_from_coordinates
from telegram import InlineKeyboardMarkup as tg_InlineKeyboardMarkup
from telegram import error as tg_error


@bot.bot_logger()
@bot.save_current_state
def start_reg(update, _):
    update.message.reply_text(
        "Отличное решение!\n"
        "После регистрации вы сможете не только смотреть анкеты,\nно и сами станете доступны для поиска.\n"
        "Во время регистрации я у вас спрошу имя, цель (общение или знакомство), пол, возраст, фото и комментарий.",
        reply_markup=keyboards.keyboard_for_start)
    return 0


@bot.bot_logger()
@bot.check_limit(limit=64)
@bot.save_current_state
def start_reg_handler(update, context):
    context.user_data['NewUser'] = classes.NewUser(tg_user_id=update.effective_user.id)
    update.message.reply_text('Шаг 1 из 7.\nКак вас зовут?',
                              reply_markup=keyboards.keyboard_for_user_name(name=update.effective_user.username))
    return 1


@bot.bot_logger()
@bot.check_limit(limit=64)
@bot.save_current_state
def user_name_handler(update, context):
    message_text = update.message.text.lower().strip()
    if message_text.startswith('использовать имя аккаунта'):
        context.user_data['NewUser'].name = update.effective_user.username  # Get first and last name of user
    else:
        context.user_data['NewUser'].name = message_text
    update.message.reply_text(f'Шаг 2 из 7.\nВы хотите общаться или знакомиться?',
                              reply_markup=keyboards.keyboard_for_user_goal)
    return 2


@bot.bot_logger()
@bot.check_limit(limit=100)
@bot.save_current_state
def user_goal_handler(update, context):
    message_text = update.message.text.lower().strip()
    if message_text == 'общаться':
        context.user_data['NewUser'].goal = 1  # Conversation
    elif message_text == 'знакомиться':
        context.user_data['NewUser'].goal = 2  # Dating
    elif message_text == 'общаться и знакомиться':
        context.user_data['NewUser'].goal = 3  # Both
    elif not config.back_r.match(message_text):
        update.message.reply_text(f'Я вас не понимаю. Напишиете "Общаться", "Знакомиться" или "Общаться и Знакомиться"')
        return 2
    update.message.reply_text(f'Шаг 3 из 7.\nУкажите ваш пол.', reply_markup=keyboards.keyboard_for_user_gender)
    return 3


@bot.bot_logger()
@bot.check_limit(limit=100)
@bot.save_current_state
def user_gender_handler(update, context):
    # # # PROCESS OLD MESSAGE # # #
    message_text = update.message.text.lower().strip()
    if message_text == 'я парень':
        context.user_data['NewUser'].gender = 1  # Male
    elif message_text == 'я девушка':
        context.user_data['NewUser'].gender = 2  # Female
    elif not config.back_r.match(message_text):  # gender is required, no skip_r
        update.message.reply_text(f'Я вас не понимаю Напишите "Я парень" или "Я девушка"')
        return 3
    # # # SEND NEW MESSAGE # # #
    update.message.reply_text(f'Шаг 4 из 7.\nУкажите ваш возраст.',
                              reply_markup=keyboards.keyboard_for_user_age)
    return 4


@bot.bot_logger(text='Не могу схранить ваш возраст, неизвестная ошибка. Пропускаю этот шаг.')
@bot.check_limit(limit=100)
@bot.save_current_state
def user_age_handler(update, context):
    message_text = update.message.text.lower().strip()
    if not config.back_r.match(message_text):
        try:
            age = int(''.join([letter for letter in message_text if letter.isdigit()]))
            if 9 < age < 100:
                context.user_data['NewUser'].age = age
            else:
                raise AssertionError
        except (ValueError, AssertionError):  # If can't convert str to int
            update.message.reply_text(f'Я вас не понимаю Напишите Свой возраст. Например: "25 лет."')
            return 4
    if update.message.chat.type != 'group':  # No location for public chat FIXME no question if chat are public
        update.message.reply_text(f'Шаг 5 из 7.\nНапишите вашу страну и город через запятую.',
                                  reply_markup=keyboards.keyboard_for_user_location)
    return 5


@bot.bot_logger()
@bot.check_limit(limit=100)
@bot.save_current_state
def user_location_handler(update, context):  # user_city don't have validation
    """
    Maybe no necessary to get the country from the location, as the country may be determined incorrectly ?
    Maybe no need to get city from the location, as the user may want to specify only a country ?
    """
    # # # PROCESS OLD MESSAGE # # #
    message_text = update.message.text.lower().strip() if update.message.text else None
    if update.message.location:
        country, city = get_location_from_coordinates(update.message.location)  # [city, country]
        context.user_data['NewUser'].country, context.user_data['NewUser'].city = country, city
    elif not (config.back_r.match(message_text) or config.skip_r.match(message_text)):
        # If not enough values (if user missed a ',') - var with asterisk will be an empty list
        country, *city = update.message.text.strip().split(',', maxsplit=2)
        context.user_data['NewUser'].country, context.user_data['NewUser'].city = ''.join(country), ''.join(city)
    update.message.reply_text(f'Шаг 6 из 7.\n'
                              'Прикрепите одну или несколько фотографий во вложении, '
                              'которые будут отображаться вместе с вашей анкетой.'
                              'Первая добавленная фотография станет вашим аватаром.\n'
                              'Когда закончите напишите "готово".',
                              reply_markup=context.user_data['NewUser'].current_keyboard)
    return 6


def add_photo(update, context):
    """
    Send answer only for first photo (if user send multiple photos at once)
    update_message.media_group_id exists only for group photo, not single photo and not text
    """
    new_user = context.user_data['NewUser']
    if len(new_user.tg_photos) < 10:  # 10 - Is also max count of photos to send at one message
        new_user.tg_photos.append(update.message.photo[-1].file_id)
        if update.message.media_group_id != new_user.old_media_group_id or update.message.media_group_id is None:
            update.message.reply_text('Добавил. Вы можете добавить еще фотографии.',
                                      reply_markup=new_user.current_keyboard)
            new_user.old_media_group_id = update.message.media_group_id  # update old_id
    else:
        update.message.reply_text('Максимальное количество фотографий: 10', reply_markup=new_user.current_keyboard)


@bot.bot_logger('Не могу сохранить ваши фотографии.')
@bot.save_current_state
def user_photos_handler(update, context):
    # # # PROCESS OLD MESSAGE # # #
    message_text = update.message.text.lower().strip() if update.message.text else None
    # Change keyboard only if 'use_account_photos' not used.
    if message_text == 'использовать фотографии профиля':
        if photos := update.effective_user.get_profile_photos().photos:  # photos of user account
            context.user_data['NewUser'].current_keyboard = keyboards.after_using_account_photos
            for photo in photos:
                update.message.photo = photo
                update.message.media_group_id = not None  # TO handle photos as group photos
                add_photo(update=update, context=context)
        else:
            update.message.reply_text('У вашего профиля нет фотографий.')
        # just to no handle if no photos. User may safely abuse this option;
        return 6
    elif message_text == 'удалить выбранные фотографии':
        if context.user_data['NewUser'].tg_photos:
            context.user_data['NewUser'].tg_photos.clear()
            context.user_data['NewUser'].current_keyboard = keyboards.original_photo_keyboard
            update.message.reply_text('Удалено. Вы можете добавить еще фотографии.',
                                      reply_markup=keyboards.original_photo_keyboard)
        else:
            update.message.reply_text('У вас нет добавленных фотографий',
                                      reply_markup=keyboards.original_photo_keyboard)
        return 6
    elif message_text != 'готово' and not (config.back_r.match(message_text) or config.skip_r.match(message_text)):
        update.message.reply_text(f'Я вас не понимаю. Напишите "Готово" что-бы перейти к следующему шагу')
        return 6
    # # # SEND NEW MESSAGE # # #
    update.message.reply_text(f'Шаг 7 из 7.\nРасскажите о себе.\nМаксимальное количество символов - 500.',
                              reply_markup=keyboards.standard_keyboard)
    return 7


@bot.bot_logger(text='Не могу показать профиль.')
@bot.check_limit(limit=500)
@bot.save_current_state
def user_comment_handler(update, context):
    message_text = update.message.text.lower().strip()
    if not (config.back_r.match(message_text) or config.skip_r.match(message_text)):
        context.user_data['NewUser'].comment = message_text
    # # # SEND NEW MESSAGE # # #
    update.message.reply_text('Так будет выглядеть ваш профиль:', reply_markup=keyboards.keyboard_for_user_confirm)
    context.user_data['NewUser'].show_profile(show_to_id=update.effective_user.id)
    return 8


@bot.bot_logger('Не могу сохранить ваш профиль. Отменяю регистрацию.')
@bot.save_current_state
def user_confirm_handler(update, context):
    message_text = update.message.text.lower().strip()
    if message_text == 'завершить':
        context.user_data['NewUser'].create_user()
        del context.user_data['NewUser']  # del object after insertion to not admit memory leak
        update.message.reply_text('Поздравляю, вы успешно зарегистрированы!\n\n'
                                  'Что еще можно сделать?\n'
                                  f'{config.commands}')
    else:
        update.message.reply_text('"Напишиете завершить" для завершения регистрации,\n'
                                  '"Назад" если хотите внести изменения и "Отмена" для отмены регистарции')
        return 8
    return bot.end_conversation()


@bot.bot_logger()
@bot.save_current_state
def start_search(update, _):
    update.message.reply_text('Привет! Я бот по имени Ruby. Я могу найти тебе пару для знакомства или общения.',
                              reply_markup=keyboards.keyboard_for_start)
    return 0


@bot.bot_logger()
@bot.save_current_state
def start_search_handler(update, context):
    context.user_data['TargetUser'] = classes.TargetUser(tg_user_id=update.effective_user.id)
    if not context.user_data['TargetUser'].my_votes:  # No likes - no search :)
        update.message.reply_text(
            "Вы не оценили ни 1 пост поэтому мы не можем подобрать вам никого по общим интересам.\n"
            'Используйте команду /get_post что-бы оценить посты.',
            reply_markup=keyboards.remove_keyboard())
        return bot.end_conversation()
    elif not context.user_data['TargetUser'].current_matches:  # If user have not matches at all
        update.message.reply_text('Вы оценили слишком мало постов,\n'
                                  'поэтому у вас нет ни одного совпадения по общим интересам.\n'
                                  'Оцените больше постов тогда у вас появятся совпадения.\n'
                                  'Используйте команду /get_post что-бы оценить больше постов.',
                                  reply_markup=keyboards.remove_keyboard())
        return bot.end_conversation()
    else:
        update.message.reply_text('вы хотите общаться или знакомиться?', reply_markup=keyboards.keyboard_for_match_goal)
    return 1


@bot.bot_logger()
@bot.save_current_state
def target_goal_handler(update, context):
    # # # PROCESS OLD MESSAGE # # #
    message_text = update.message.text.lower().strip()
    if message_text == 'хочу общаться':
        context.user_data['TargetUser'].goal = (1,)  # Conversation; must be tuple
    elif message_text == 'хочу знакомиться':
        context.user_data['TargetUser'].goal = (2,)  # Dating; must be tuple
    elif message_text == 'общаться и знакомиться':
        context.user_data['TargetUser'].goal = (1, 2, 3,)  # female male or both; must be tuple
    else:
        update.message.reply_text('Напишите "Знакомиться", "Общаться" или "Знакомиться и Общаться"')
        return
    context.user_data['TargetUser'].use_goal_filter()
    # # # SEND NEW MESSAGE # # #
    update.message.reply_text('Выберите желаемый пол партнера', reply_markup=keyboards.keyboard_for_match_gender)
    return 2


@bot.bot_logger()
def target_gender_handler(update, context):
    # # # PROCESS OLD MESSAGE # # #
    message_text = update.message.text.lower().strip()
    if message_text == 'парень':
        context.user_data['TargetUser'].gender = (1,)  # Female; must be tuple
    elif message_text == 'девушка':
        context.user_data['TargetUser'].gender = (2,)  # Male; must be tuple
    elif message_text == 'любой пол':
        context.user_data['TargetUser'].gender = (1, 2, 3,)  # Any; must be tuple
    else:
        update.message.reply_text('Я вас не понимаю. Напишите "Парень", "Девушка" или "Любой пол"')
        return
    context.user_data['TargetUser'].use_gender_filter()
    # # # SEND NEW MESSAGE # # #
    update.message.reply_text('Выберите желаемый возраст. Вы можете выбрать диапазон казав 2 числа через дефис, '
                              'например 24 - 38.',
                              reply_markup=keyboards.keyboard_for_match_age)
    return 3


@bot.bot_logger(end=True, text='Не могу выполнить поиск партнера, завершаю поиск.')
def target_age_handler(update, context):
    try:
        # # # PROCESS OLD MESSAGE # # #
        if update.message:
            message_text = update.message.text.lower().strip()
            age = ''.join([letter for letter in message_text if letter.isdigit()])
            if age and len(age) <= 2 and 0 <= int(age) < 100:  # If two digits; int(00) == 0
                context.user_data['TargetUser'].age_range = int(age), int(age)
            elif age and len(age) <= 4 and 0 <= int(age[:2]) < int(age[2:]):  # If four digits (range of ages);
                context.user_data['TargetUser'].age_range = int(age[:2]), int(age[2:])
            elif 'любой' in message_text:
                context.user_data['TargetUser'].age_range = 10, 99  # First is bigger number
            else:
                update.message.reply_text('Напишите число в формате xx, диапазон в формате xx - xx или "Любой возраст"')
                return
            context.user_data['TargetUser'].use_age_filter()
    except Exception as e:
        update.message.reply_text('Не могу применить фильтр по возрасту, неизвестная ошибка. Пропускаю шаг.')
        logger.error(f'Error in target_age_handler during handling an old message, {e}')
    # # # SEND NEW MESSAGE # # #
    if context.user_data['TargetUser'].set_matches():  # If user has matches
        context.user_data['TargetUser'].set_new_matches()
        bot.remove_keyboard(update=update)
        bot.send_message(
            chat_id=update.effective_user.id,
            text=f"Найдено {context.user_data['TargetUser'].current_matches_count} совпадений.\n"
                 f"Предложения по добавлению новых фильтров пишите пожалуйста ему @david_shiko",
            reply_markup=keyboards.keyboard_for_additional_filters(
                len_all_matches=context.user_data['TargetUser'].current_matches_count,
                len_new_matches=context.user_data['TargetUser'].new_matches_count))
    else:
        update.message.reply_text('К сожалению, мы никого не смогли найти по заданным фильтрам.',
                                  reply_markup=keyboards.remove_keyboard())
    return 4


@bot.bot_logger()
def target_show_match_handler(update, context):
    if context.user_data['TargetUser'].flag:  # Flag is just for user convenience
        message_text = update.message.text.lower().strip()
        # if message_text == 'новый поиск':  # TODO keyboard refactoring requiring
        #     return start_search(update, context)  # Function will return a return code 
        if message_text == 'еще':
            context.user_data['TargetUser'].show_match()
        elif message_text == 'завершить':
            update.message.reply_text('Завершено. До новых встреч!', reply_markup=keyboards.remove_keyboard())
            return bot.end_conversation()
        else:
            update.message.reply_text('Я вас не понимаю. Напишите "Еще" или "Завершить"')
    else:
        update.message.reply_text('Я вас не понимаю. Нажмите на 1-у из кнопок, "Показать всех" или "Показать новых".')
    return 4


def create_post(update, _):
    if crud.read_user(tg_user_id=update.effective_user.id):
        text = ("Создавая посты вы помогаете развиваться сообществу! Прикрепите аудио,"
                "видео, фото или текст к посту и добавьте подпись, что бы пост был красочнее!")
        reply_markup = keyboards.remove_keyboard()  # Remove previous keyboard (if exists)
    else:
        text = 'Только зарегистрированные пользвоатели могут создавать посты'
        reply_markup = keyboards.keyboard_reg
    update.message.reply_text(text=text, reply_markup=reply_markup)
    return 0


def compose_post_handler(update, context):  # Not in use
    """
    telegram has bot.send_media_group method to send message with multiple attachments,
    but documents and audios can't be mixed with another type of attachments.
    Example of code:
    bot.send_media_group(chat_id=177381168, media=[tg_InputMediaDocument(update.message.document, caption='123'),
                                                   tg_InputMediaPhoto(update.message.photo[-1], caption='456')])
    So I just sending multiple messages one by one.
    """
    message_text = update.message.text.lower().strip()
    if message_text == 'готово':
        return 1
    else:
        # media_type = tg_utils_helpers.effective_message_type(update.message)
        context.user_data['Post'].messages.append(update.message)
        return


@bot.bot_logger(text='Не могу создать пост', end=True)
def show_sample_handler(update, context):
    """
    telegram has bot.send_media_group method to send message with multiple attachments,
    but documents and audios can't be mixed with another type of attachments.
    Example of code:
    bot.send_media_group(chat_id=177381168, media=[tg_InputMediaDocument(update.message.document, caption='123'),
                                                   tg_InputMediaPhoto(update.message.photo[-1], caption='456')])
    So I just sending multiple messages one by one.
    """
    # 3 cases: Message without attachment. Message with attachment and caption. Message only with attachment
    context.user_data['Post'] = classes.Post(caption=(update.message.text or update.message.caption or ''))
    update.message.reply_text('Ваш пост будет выглядеть вот так, отправить?', reply_markup=keyboards.keyboard_for_post)
    sent_message = bot.copy_message(
        chat_id=update.effective_user.id,  # I don't know why need user_id and not config.bot_id,
        from_chat_id=update.effective_user.id,
        message_id=update.message.message_id,
        caption=f"{context.user_data['Post'].caption}{context.user_data['Post'].default_caption}",
        reply_markup=keyboards.get_poll_keyboard(post_id=context.user_data['Post'].post_id,
                                                 pattern='',
                                                 likes_count=0,
                                                 dislikes_count=0))  # 0 for sample)
    context.user_data['Post'].message_id = sent_message.message_id
    return 1


@bot.bot_logger('не удалось создать пост')
def post_confirm_handler(update, context):
    if 'отправить' in update.message.text.lower().strip():
        context.user_data['Post'].create_post(tg_user_id=update.effective_user.id,
                                              message_id=context.user_data['Post'].message_id)
        del context.user_data['Post']  # del object after insertion to not admit memory leak
        update.message.reply_text('Успех! Спасибо, что помогаете развиваться сообществу!',
                                  reply_markup=keyboards.remove_keyboard())
        return bot.end_conversation()
    else:
        update.message.reply_text('Я вас не понимаю. Напишите "Отправить" или "Отмена"')
        return


@bot.bot_logger()
def send_posts(update, _):  # fixme use message queue to send more that 20 messages to different users!
    post = classes.Post(recipient=all)
    for tg_user_id in [tg_user[0] for tg_user in crud.read_users()]:
        try:
            sent_message = bot.copy_message(
                chat_id=tg_user_id,  # I don't know why need user_id and not config.bot_id,
                from_chat_id=update.effective_user.id,
                message_id=post.post_message_id,
                caption=f"{post.caption}{post.default_caption}",
                reply_markup=keyboards.get_poll_keyboard(post_id=post.post_id,
                                                         likes_count=post.likes_count,
                                                         dislikes_count=post.dislikes_count))

            # Assigning message_id to a user vote after sending a message (special for telegram)
            post.save_shown_post(tg_user_id=tg_user_id, post_message_id=sent_message.message_id)
        except (tg_error.Unauthorized, tg_error.BadRequest):
            crud.delete_user(tg_user_id=tg_user_id)


@bot.bot_logger()
def get_post(update, _):  # TODO error logger; Not in use
    post = classes.Post(recipient=update.effective_user.id)
    if post:
        sent_message = bot.copy_message(
            chat_id=update.effective_user.id,  # I don't know why need user_id and not config.bot_id,
            from_chat_id=update.effective_user.id,
            message_id=post.post_message_id,
            caption=f"{post.caption}{post.default_caption}",
            reply_markup=keyboards.get_poll_keyboard(post_id=post.post_message_id,
                                                     pattern='vote',
                                                     likes_count=post.likes_count,
                                                     dislikes_count=post.dislikes_count))
        post.save_shown_post(tg_user_id=update.effective_user.id, post_message_id=sent_message.message_id)
    else:
        update.message.reply_text(text='Отличная работа, вы оценили все посты!',
                                  reply_markup=keyboards.remove_keyboard())


def post_vote_handler(update, _):
    """
    If user pressed button from forwarded message (default disable):
    https://stackoverflow.com/q/46756643/11277611
    """
    data = update.callback_query.data.split()[-1]  # list, data: pattern + post_id
    vote = 1 if int(data) > 0 else -1  # Data is a pos or neg post_id (if user not abused it)
    post = classes.Post(post_id=abs(int(data)))

    if post.set_vote(tg_user_id=update.effective_user.id, post_id=post.post_id, new_vote=vote):
        for tg_user_id in [i[0] for i in crud.read_users()]:  # TODO add delay
            post_message_id = crud.read_vote(tg_user_id=tg_user_id, post_id=post.post_id)[1]
            try:
                bot.edit_message_reply_markup(chat_id=tg_user_id,
                                              message_id=post_message_id,
                                              reply_markup=keyboards.get_poll_keyboard(
                                                  post_id=post.post_id,
                                                  likes_count=post.likes_count,
                                                  dislikes_count=post.dislikes_count))
            except (tg_error.Unauthorized, tg_error.BadRequest) as e:
                crud.delete_user(tg_user_id=tg_user_id)
            except Exception as e:
                logger.error(f'Error in post_vote_handler during vote update, {e}')
    update.callback_query.answer()  # To break down a "wait" indicator


@bot.bot_logger('не удалось применить фильтр. Фильтры применены не будут')
def additional_filters_handler(update, context):
    if 'TargetUser' not in context.user_data:  # Accept callback only if user is inside a conversation
        update.callback_query.message.reply_text(
            'Фильтры доступны только во время поиска партнера. Что бы начать поиск напишите "/start"',
            reply_markup=keyboards.keyboard_start)
        update.callback_query.answer()
        return
    user = context.user_data['TargetUser']  # action (button_name) and flag
    button_name, old_flag = update.callback_query.data.split()  # button_name is str, old_flag is bool
    if button_name == 'hide':
        update.callback_query.edit_message_reply_markup(
            reply_markup=keyboards.keyboard_for_additional_filters(
                len_new_matches=user.new_matches_count,
                len_all_matches=user.current_matches_count))
    elif button_name == 'show':
        update.callback_query.edit_message_reply_markup(
            reply_markup=keyboards.keyboard_for_additional_filters(
                len_new_matches=user.new_matches_count,
                len_all_matches=user.current_matches_count,
                checkboxes=user.checkboxes))
    elif button_name == 'apply':
        old_current_matches_count, old_new_matches_count = user.current_matches_count, user.new_matches_count
        user.set_matches(reset_checkboxes=True)  # reset to drop old table; count_matches is updated
        user.set_new_matches()  # No reset flag because no table creation internally
        if (user.current_matches_count, user.new_matches_count) != (old_current_matches_count, old_new_matches_count):
            update.callback_query.edit_message_reply_markup(
                reply_markup=keyboards.keyboard_for_additional_filters(
                    len_new_matches=user.new_matches_count,
                    len_all_matches=user.current_matches_count,
                    checkboxes=user.checkboxes))  # Edit markup to update shown count of matches
    elif button_name == 'all':  # Flag is just for user convenience
        user.current_matches, context.user_data['TargetUser'].flag = user.current_matches, True
        user.show_match()
    elif button_name == 'new':  # Flag is just for user convenience
        user.current_matches, context.user_data['TargetUser'].flag = user.new_matches, True
        user.show_match()
    elif button_name in user.checkboxes:  # TODO fix me
        current_keyboard = update.callback_query.message.reply_markup.inline_keyboard  # Buttons of incoming keyboard
        keyboard_button = bot.get_keyboard_button_by_callback_data(keyboard=current_keyboard,
                                                                   button_callback_data=update.callback_query.data)[0]
        new_keyboard = keyboards.toggle_checkbox(current_keyboard, keyboard_button, old_flag)
        update.callback_query.edit_message_reply_markup(tg_InlineKeyboardMarkup(new_keyboard))
    update.callback_query.answer()


def go_back(update, context):
    f = [start_reg, start_reg_handler, user_name_handler, user_goal_handler, user_gender_handler, user_age_handler,
         user_location_handler, user_photos_handler, user_comment_handler, user_confirm_handler]
    return f[context.user_data['current_state'] - 1](update, context)


def go_next(update, context):
    f = [start_reg, start_reg_handler, user_name_handler, user_goal_handler, user_gender_handler, user_age_handler, ]
    if context.user_data['current_state'] in (4, 5):  # Skipping allow only for step 3
        return f[context.user_data['current_state']](update, context)
