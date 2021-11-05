from telegram.utils import request as tg_utils_request
from telegram import ReplyKeyboardRemove as tg_ReplyKeyboardRemove
from telegram import InlineKeyboardButton as tg_InlineKeyboardButton
from telegram import InlineKeyboardMarkup as tg_InlineKeyboardMarkup
from telegram import Bot
from telegram import error as tg_error
from config import tg_bot_token
from postconfig import logger


class Bot(Bot):

    def __init__(self, token, request):
        super().__init__(token=token, request=request)

    @staticmethod
    def check_limit(limit: int):
        def decorator(function):
            def wrapper(*args, **kwargs):
                update = args[0]
                len_text = len(update.message.text) if update.message.text else 0  # "0", not False!
                if len_text < limit:
                    return function(*args, **kwargs)
                else:
                    update.message.reply_text(f'Слишком много символов.\n'
                                              f'Допустимое количество символов: {limit}.\n'
                                              f'Вы использовали символов: {len_text}')

            return wrapper

        return decorator

    @staticmethod
    def bot_logger(text: str = '', end: bool = False):
        def decorator(function):
            def wrapper(*args, **kwargs):
                update = args[0]
                # if args:
                #     update_message_reply_text = args[0]
                # elif 'update_message' in kwargs:
                #     update_message_reply_text = kwargs['update_message'].reply_text
                # elif 'update_message_reply_text' in kwargs:
                #     update_message_reply_text = kwargs['update_message_reply_text']
                # elif 'reply_text' in kwargs:
                #     update_message_reply_text = kwargs['reply_text']
                # else:
                #     update_message_reply_text = lambda text: logger.warning('Incorrect "bot_logger" function usage,'
                #                                                             'Can not notify user about exception!')
                try:
                    return function(*args, **kwargs)
                except Exception as e:
                    update.message.reply_text(text=f'Неизвестная ошибка. {text} Попробуйте повторить попытку позднее')
                    logger.error(e)
                    return -1 if end else None

            return wrapper

        return decorator

    @staticmethod
    def save_current_state(function):
        def decorator(*args, **kwargs):
            current_state = args[1].user_data['current_state'] = function(*args, **kwargs)  # args[1] is are context
            return current_state

        return decorator

    @staticmethod
    def end_conversation(update=None, context=None):  # Maybe move it to user anf ancestor from bot?
        if update:
            update.message.reply_text('Галя, неси ключ, у нас отмена! Отменено.', reply_markup=tg_ReplyKeyboardRemove())
        del context.chat_data
        return -1  # Any version of NEG_ONE

    @staticmethod
    def combined_decorators(self, decorators_kwargs: dict[dict[list]]):
        def decorator(function):
            def wrapper(*args, **kwargs):
                if 'bot_logger' in decorators_kwargs:
                    function = self.bot_logger(text=decorators_kwargs['text'], end=decorators_kwargs['end'])()
                if 'save_current_state' in decorators_kwargs:
                    function = self.save_current_state(function)
                if 'check)limit' in decorators_kwargs:
                    function = self.check_limit(limit=decorators_kwargs['limit'])()
                    return function(*args, **kwargs)

            return wrapper

        return decorator

    def remove_keyboard(self, update, _=None):
        sent_message = update.message.reply_text('Пасхалка: Что-бы удалить кнопки (вместо клавиатуры) - '
                                                 'нужно отправить новое сообщение без кнопок и тут же его удалить',
                                                 reply_markup=tg_ReplyKeyboardRemove())
        self.delete_message(chat_id=update.effective_user.id, message_id=sent_message.message_id, )

    @staticmethod
    def get_keyboard_button_by(keyboard: list[list[tg_InlineKeyboardButton]], pattern: str, by: str) -> list[dict]:
        result = []
        for x, button_keyboard_row_index in enumerate(keyboard):  # Iterate over keyboard rows
            for y, button in enumerate(button_keyboard_row_index):  # Iterate over buttons of row
                if getattr(button, by) == pattern:
                    result.append({'button_keyboard_index': x, 'button_row_index': y, 'button': button})
        return result

    def get_keyboard_button_by_callback_data(self,
                                             keyboard: list[list[tg_InlineKeyboardButton]],
                                             button_callback_data: str) -> list[dict]:
        return self.get_keyboard_button_by(keyboard=keyboard, pattern=button_callback_data, by='callback_data')

    # @staticmethod
    # def get_inline_button_by_callback_data(keyboard: list[list[tg_InlineKeyboardButton]],
    #                                        button_callback_data: str) -> dict:
    #     result = []
    #     for i, button_keyboard_row_index in enumerate(keyboard):  # Iterate over keyboard rows
    #         for button_row_index, button in enumerate(button_keyboard_row_index):  # Iterate over buttons of row
    #             if button.callback_data == button_callback_data:
    #                 result.append({'button_keyboard_row_index': button_keyboard_row_index,
    #                                'button_row_index': button_row_index,
    #                                'button': button})
    #     return result


request = tg_utils_request.Request(connect_timeout=3, read_timeout=3, con_pool_size=16)
bot = Bot(token=tg_bot_token, request=request)  # base_url=config.TG_PROXY_URL)
