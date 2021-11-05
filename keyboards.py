import config
from telegram import ReplyKeyboardMarkup as tg_RKM
from telegram import InlineKeyboardMarkup as tg_IKM
from telegram import InlineKeyboardButton as tg_IKB
from telegram import KeyboardButton as tg_KB
from telegram import ReplyKeyboardRemove as tg_ReplyKeyboardRemove


def get_poll_keyboard(post_id: int, likes_count: int, dislikes_count: int,
                      pattern: str = 'vote') -> tg_IKM:
    """
    This is keyboard for appending to the post and voting.
    TG can accept only str callback data. Like = +post_id, dislike = -post_id.
    :rtype: object
    """
    return tg_IKM([[
        tg_IKB(text=f'👎 {dislikes_count}', callback_data=f'{pattern} -{post_id}'),
        tg_IKB(text=f'👍 {likes_count}', callback_data=f'{pattern} +{post_id}'), ]])


emoji_checkboxes = ['🔲', '☑']


class EmojiCheckboxes:
    checked = '☑'
    unchecked = '🔲'

    @staticmethod
    def toggle_checkbox(keyboard, keyboard_button, old_flag):
        x, y = keyboard_button['button_keyboard_index'], keyboard_button['button_row_index']
        keyboard[x][y].callback_data = f"{keyboard_button['button'].callback_data.replace(old_flag, not old_flag)}"
        keyboard[x][y].text = f"{keyboard_button['button'].text.replace(old_flag, not old_flag)}"
        return keyboard


# COMMON KEYBOARDS THAT NO REQUIRES ARGUMENTS'
keyboard_start = tg_RKM(
    [['/start']],
    resize_keyboard=True,
    one_time_keyboard=True)

keyboard_reg = tg_RKM([['/reg']], resize_keyboard=True, one_time_keyboard=True)
keyboard_go_or_cancel = tg_RKM(keyboard=[['Поехали'], ['Отмена']], resize_keyboard=True, one_time_keyboard=True)
keyboard_for_post = tg_RKM(keyboard=[['Отправить'], ['Отмена']], resize_keyboard=True, one_time_keyboard=True)

original_photo_keyboard = tg_RKM(
    keyboard=[['Готово'], ['Использовать фотографии профиля'], ['Назад'], ['Отмена']],
    resize_keyboard=True, one_time_keyboard=True)
before_using_account_photos = tg_RKM(
    keyboard=[['Готово'], ['Использовать фотографии профиля'], ['Удалить выбранные фотографии'], ['Назад', 'Отмена']],
    resize_keyboard=True, one_time_keyboard=True)
after_using_account_photos = tg_RKM(
    keyboard=[['Готово'], ['Удалить выбранные фотографии'], ['Назад', 'Отмена']],
    resize_keyboard=True, one_time_keyboard=True)

keyboard_for_start = tg_RKM(keyboard=[['Поехали!'], ['Отмена']], resize_keyboard=True, one_time_keyboard=True)
keyboard_for_user_name = lambda name: tg_RKM(
    keyboard=[[f'Использовать имя аккаунта ("{name}")'], ['Отмена']],
    resize_keyboard=True, one_time_keyboard=True)
keyboard_for_user_goal = tg_RKM(
    keyboard=[['Общаться', 'Знакомиться'], ['Общаться и знакомиться'], ['Назад', 'Отмена']],
    resize_keyboard=True, one_time_keyboard=True)
keyboard_for_user_gender = tg_RKM(
    keyboard=[['Я девушка', 'Я парень'], ['Назад'], ['Отмена']],
    resize_keyboard=True, one_time_keyboard=True)
keyboard_for_user_age = standard_keyboard = tg_RKM(
    keyboard=[['Назад'], ['Отмена']], resize_keyboard=True, one_time_keyboard=True)
keyboard_for_user_location = tg_RKM(
    keyboard=[[tg_KB(text="Отправить местоположение", request_location=True)], ['Назад', 'Пропустить'], ['Отмена']],
    resize_keyboard=True, one_time_keyboard=True)
keyboard_for_user_confirm = tg_RKM(
    keyboard=[['Назад', 'Завершить'], ['Отмена']],
    resize_keyboard=True, one_time_keyboard=True)

keyboard_for_match_goal = tg_RKM(
    keyboard=[['Хочу знакомиться', 'Хочу общаться'], ['Общаться и знакомиться'], ['Отмена']],
    resize_keyboard=True, one_time_keyboard=True)
keyboard_for_match_gender = tg_RKM(
    keyboard=[['Парень', 'Девушка'], ['Любой пол'], ['Назад', 'Отмена']],
    resize_keyboard=True, one_time_keyboard=True)
keyboard_for_match_age = tg_RKM(
    keyboard=[['Любой возраст'], ['Назад', 'Отмена']],
    resize_keyboard=True, one_time_keyboard=True)

# keyboard_for_new_search = tg_RKM(
#     keyboard=[['Новый поиск'], ['Завершить']],
#     resize_keyboard=True, one_time_keyboard=True)
keyboard_for_votes = tg_RKM(  # Not in use
    keyboard=[['Оценить посты', 'Отмена']],
    resize_keyboard=True, one_time_keyboard=True)
keyboard_for_one_more_match = tg_RKM(
    keyboard=[['Еще'], ['Завершить']],
    resize_keyboard=True, one_time_keyboard=True)

remove_keyboard = tg_ReplyKeyboardRemove


def keyboard_for_additional_filters(len_all_matches: int, len_new_matches: int, checkboxes: dict = None):
    rows_buttons = [
        [tg_IKB(text='Показать дополнительные фильтры', callback_data=f'checkboxes show True')],
        [tg_IKB(text=f'Показать всех ({len_all_matches})', callback_data=f'checkboxes all True')],
        [tg_IKB(text=f'Показать новых ({len_new_matches})', callback_data=f'checkboxes new True')]
    ]
    if not checkboxes:  # checkboxes as indicator to add hidden buttons
        return
    emojis = {checkbox: emoji_checkboxes[1] if flag else emoji_checkboxes[0] for checkbox, flag in checkboxes}
    flags = {checkbox: True if flag else False for checkbox, flag in checkboxes}
    btn_1 = tg_IKB(text=f"Скрыть дополнительные фильтры", callback_data=f'checkboxes hide True')
    btn_2 = tg_IKB(text=f"{emojis['age']} Возраст указан", callback_data=f"checkboxes age {checkboxes['age']}"),
    btn_3 = tg_IKB(text=f"{emojis['country']} Страна указана", callback_data=f"checkboxes country {flags['country']}")
    btn_4 = tg_IKB(text=f"{emojis} Город указан  ", callback_data=f"checkboxes city {flags['city']}")
    btn_5 = tg_IKB(text=f"{emojis} С фотографией", callback_data=f"checkboxes photo {flags['photo']}")
    btn_6 = [tg_IKB(text=f"Применить фильтры", callback_data=f'checkboxes apply True')]
    return tg_IKM([btn_1, [btn_2, btn_3], [btn_4, btn_5], btn_6])


def keyboard_for_show_matches(len_all_matches, len_new_matches):
    return tg_RKM(
        keyboard=[[f"Показать всех ({len_all_matches})", f"Показать новых ({len_new_matches})"],
                  ['Назад'], ['Отмена']], resize_keyboard=True, one_time_keyboard=True)
