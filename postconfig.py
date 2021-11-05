from loguru import logger
from os import uname as os_uname
import psycopg2
from config import db_name, db_user, db_password, db_connection_timeout


class DBConnectionManager:
    """
    What if connection are closed during an operation? Maybe check remain timeout?
    """
    def __init__(self):
        self.global_connection = self.get_connection(connection_timeout=0)

    @staticmethod
    def get_connection(connection_timeout: int = db_connection_timeout):
        connection = psycopg2.connect(dbname=db_name,
                                      user=db_user,
                                      password=db_password,
                                      host='127.0.0.1',
                                      port="5432",
                                      connect_timeout=connection_timeout)
        connection.autocommit = True
        return connection

    def assign_connection(self, connection):
        if not connection or connection.closed:
            return self.get_connection()


global_connection = DBConnectionManager.get_connection()

logger.add(sink="/home/guest/rubik_tg_bot/log_error.txt" if os_uname()[1] != 'david-ThinkPad-E480' else "log_error.txt",
           filter=lambda record: record["level"].name == "ERROR", backtrace=True,
           format="{time} {level} {message}", level="INFO", rotation="1 MB", compression="zip")


def error_logger(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            logger.error(f'{e}')

    return wrapper
