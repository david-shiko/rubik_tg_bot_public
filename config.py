import re


"""
TODO use env
"""


DEBUG = True
bot_id = 838004799
db_name = 'rubik_tg_bot_db'
db_user = 'rubik_tg_bot_user'
db_host = 'localhost'
db_connection_timeout = 1800

DEFAULT_PHOTO = 'AgADAgADWqwxG2mlAAFIDtF_p9eVWNcS2bkPAAQBAAMCAAN4AAMKFQcAARYE'
DEFAULT_POST_MESSAGE_ID = 45137  # Default message_id

MEN_PHOTOS_FOR_GEN = ('AgACAgIAAxkBAAKv7WFDRYye6ewbdya9j5CpdDqXa4yvAAL8sjEblVEYSlfVDEAtP5qFAQADAgADeAADIAQ',
                      'AgACAgIAAxkBAAKv9GFDR08nsBeCESoCN0OqodLmjo7bAAIFszEblVEYSkxJQl29RwoKAQADAgADbQADIAQ',
                      'AgACAgIAAxkBAAKv-GFDR4FCsv-qOE_LVROAN4XnC_rnAAIGszEblVEYSt8QHJ2RD1mRAQADAgADbQADIAQ',
                      'AgACAgIAAxkBAAKv_GFDR7tPMCMaCSuI6X0zxdAexUNZAAIOszEblVEYSlu12UC9HH62AQADAgADeQADIAQ',
                      'AgACAgIAAxkBAAKv_2FDR9rZx0COTiNyO401Jx1mfA2jAAIQszEblVEYSsTjuxcCwO30AQADAgADeAADIAQ',)

WOMEN_PHOTOS_FOR_GEN = ('AgACAgIAAxkBAAKwAmFDSGCPmA4dnG-p_cXjOq1kFaaDAAIUszEblVEYSuBnEIXwqaRKAQADAgADeAADIAQ',
                        'AgACAgIAAxkBAAKwBWFDTZ9SmvaJMwN31K3XdkEGy-DNAAIpszEblVEYSvMwbYCyiP-gAQADAgADeAADIAQ',
                        'AgACAgIAAxkBAAKwCGFDTc5q5CeR8ZmlM_nm-8B4Vp7AAAIqszEblVEYSkmdZPnGxT-cAQADAgADeAADIAQ',
                        'AgACAgIAAxkBAAKwC2FDTe0UlLQ1lrYZ0oQBRE3FYSZOAAIsszEblVEYSpovCp2vxAt2AQADAgADeAADIAQ',
                        'AgACAgIAAxkBAAKwDmFDTibPEqN6XgIeTWttQAfBpSmsAAIuszEblVEYSpyQN3nBpmiJAQADAgADbQADIAQ',)

cancel_s = r'^отмена$|^cancel$|^/cancel$'
back_s = r'^назад$|^back$'
skip_s = r'^пропустить$|^skip$'
start_reg_s = r'^регистрация$|^/reg$'
start_search_s = r'^старт$|^начать$|^/start$'
create_post_s = r'^создать$|^/create$'
conversations_s = r'/reg|/start|/create'
cancel_r = re.compile(cancel_s, re.IGNORECASE)  # No need "/", no command
back_r = re.compile(back_s, re.IGNORECASE)
skip_r = re.compile(skip_s, re.IGNORECASE)
start_reg_r = re.compile(start_reg_s, re.IGNORECASE)  # "^" - start of string, "$" - end of string
start_search_r = re.compile(start_search_s, re.IGNORECASE)
create_post_r = re.compile(create_post_s, re.IGNORECASE)
another_conversation_r = conversations_r = re.compile(conversations_s, re.IGNORECASE)  # All existing conversations
start_reg_fallbacks_r = re.compile(f'{cancel_s}|{back_s}|{skip_r}|{start_reg_s}|{conversations_s}', re.IGNORECASE)
start_search_fallbacks_r = re.compile(f'{cancel_s}|{back_s}|{start_search_s}|{conversations_s}', re.IGNORECASE)
create_post_fallbacks_r = re.compile(f'{cancel_s}|{back_s}|{create_post_s}|{conversations_s}', re.IGNORECASE)
help_r = re.compile(r'^помощь$|^/help$', re.IGNORECASE)

commands = ('/Старт - начать искать пару для общения или знакомства.\n'
            '/Регистарция - зарегистрироваться (что бы вас могли найти).\n'
            '/Создать - создать пост (в разработке).\n'
            '/Получить - получить пост (в разработке)\n')
