from postconfig import global_connection

# TODO close cursor


def read_any(table: str,
             value=None,
             select_columns: str = '*',
             column: str = None,
             fetch: str = 'fetchone',
             cursor=None) -> object:
    cursor = cursor or global_connection.cursor()
    condition = f'WHERE {column} = %s' if column else ''
    cursor.execute(f'SELECT {select_columns} FROM {table} {condition}', (value,))
    return cursor.fetchone() if fetch == 'fetchone' else cursor.fetchall()


def delete_any(table: str,
               value=None,
               column: str = None,
               cursor=None) -> object:
    cursor = cursor or global_connection.cursor()
    condition = f'WHERE {column} = %s' if column else ''
    cursor.execute(f'DELETE FROM {table} {condition}', (value,))


def create_user(tg_user_id: int,
                name: str,
                goal: str,
                gender,
                age,
                country, city: str,
                comment: str,
                photos: list,
                cursor=None) -> bool:
    cursor = cursor or global_connection.cursor()
    cursor.execute('''INSERT INTO users (tg_user_id, name, goal, gender, birthdate, country, city, comment) 
    VALUES (%s, %s, %s, %s, CURRENT_DATE - INTERVAL '%s YEAR', %s, %s, %s)''',
                   (tg_user_id, name, goal, gender, age, country, city, comment,))
    for photo in photos:
        cursor.execute('INSERT INTO photos (tg_user_id, tg_photo_file_id) VALUES (%s, %s)', (tg_user_id, photo))


def read_user(tg_user_id: int, cursor=None) -> bool:
    cursor = cursor or global_connection.cursor()
    cursor.execute('SELECT * FROM users WHERE tg_user_id = %s', (tg_user_id,))
    return True if cursor.fetchone() else False


def read_user_text_data(tg_user_id: int, cursor=None) -> bool:
    cursor = cursor or global_connection.cursor()
    cursor.execute('''SELECT 
                    name, goal, gender, 
                    DATE_PART('year', CURRENT_DATE) - DATE_PART('year', birthdate::date) as age,
                    country, city, comment 
                    FROM users 
                    WHERE tg_user_id = %s''', (tg_user_id,))
    return cursor.fetchone()


def read_user_photos(tg_user_id: int, cursor=None) -> list[str]:
    cursor = cursor or global_connection.cursor()
    cursor.execute('SELECT tg_photo_file_id FROM photos WHERE tg_user_id = %s', (tg_user_id,))
    return [photo_set[0] for photo_set in cursor.fetchall()]


def read_users(cursor=None) -> bool:
    """
    NULL if no comment (NULL equals only to NULL, no any another expression)
    """
    cursor = cursor or global_connection.cursor()
    cursor.execute("SELECT tg_user_id FROM users WHERE comment != 'bot' OR comment IS NULL")
    return cursor.fetchall()


def delete_user_photos(tg_user_id: int, cursor=None) -> bool:
    cursor = cursor or global_connection.cursor()
    cursor.execute('DELETE FROM photos WHERE tg_user_id = %s', (tg_user_id,))


def delete_user_text(tg_user_id: int, cursor=None) -> bool:
    cursor = cursor or global_connection.cursor()
    cursor.execute('DELETE FROM users WHERE tg_user_id = %s', (tg_user_id,))


def delete_user(tg_user_id: int, cursor=None) -> bool:
    cursor = cursor or global_connection.cursor()
    cursor.execute('DELETE FROM photos WHERE tg_user_id = %s', (tg_user_id,))
    cursor.execute('DELETE FROM users WHERE tg_user_id = %s', (tg_user_id,))


def create_post(tg_user_id: int, message_id: int, cursor=None) -> bool:
    cursor = cursor or global_connection.cursor()
    cursor.execute('INSERT INTO posts (tg_user_id, message_id) VALUES (%s, %s)', (tg_user_id, message_id))


def read_post(post_id: int, cursor=None) -> list:
    cursor = cursor or global_connection.cursor()
    cursor.execute('SELECT id, tg_user_id, message_id, likes_count, dislikes_count FROM posts WHERE id = %s', (post_id,))
    return cursor.fetchone()


def update_post(dict_: dict, post_id: int, cursor=None) -> bool:
    """
    DB vars (like TIME or DATE) wrapped in list of single length
    """
    cursor = cursor or global_connection.cursor()
    escaped_dict = {k: v[0] if type(k) is list else '%s' for k, v in dict_.items()}  # Replace values to "%s"
    dict_pairs_sql = ', '.join({f'{column} = {value}' for column, value in escaped_dict.items()})  # convert dict to str
    sql = f"UPDATE posts SET {dict_pairs_sql} WHERE id = %s"
    cursor.execute(sql, (*list(dict_.values()), post_id,))  # "*list - unpack and merge list with other values


def create_vote(tg_user_id: int, post_id: int, message_id: int, vote, cursor=None):
    cursor = cursor or global_connection.cursor()
    cursor.execute('INSERT INTO votes (tg_user_id, post_id, message_id, vote) VALUES (%s, %s, %s, %s)',
                   (tg_user_id, post_id, message_id, vote))


def read_vote(tg_user_id: int, post_id: int, cursor=None) -> list:
    cursor = cursor or global_connection.cursor()
    cursor.execute('SELECT vote, message_id FROM votes WHERE tg_user_id = %s AND post_id = %s', (tg_user_id, post_id),)
    return cursor.fetchone()


def update_vote(tg_user_id: int, post_id: int, dict_: dict, cursor=None) -> bool:
    """
    DB vars (like TIME or DATE) wrapped in list of single length
    """
    cursor = cursor or global_connection.cursor()
    escaped_dict = {k: v[0] if type(k) is list else '%s' for k, v in dict_.items()}  # Replace values to "%s"
    dict_pairs_sql = ', '.join({f'{column} = {value}' for column, value in escaped_dict.items()})  # convert dict to str
    sql = f"UPDATE votes SET {dict_pairs_sql} WHERE tg_user_id = %s and post_id = %s"
    cursor.execute(sql, (*list(dict_.values()), tg_user_id, post_id,))  # unpack and merge list with other values


def read_my_votes(cursor=None) -> list[tuple]:
    cursor = cursor or global_connection.cursor()
    cursor.execute('SELECT post_id, vote FROM my_votes')
    return cursor.fetchall()


def read_my_covotes(cursor=None) -> list[tuple]:
    cursor = cursor or global_connection.cursor()
    cursor.execute('SELECT tg_user_id, count_common_interests FROM my_covotes')
    return cursor.fetchall()

# def read_my_votes_count(cursor=None) -> int:
#     cursor = cursor or global_connection.cursor()
#     cursor.execute('SELECT COUNT(*) FROM my_votes')
#     return cursor.fetchone()[0]  # fetchone always returns tuple
#
#
# def read_my_covotes_count(cursor=None) -> int:
#     cursor = cursor or global_connection.cursor()
#     cursor.execute('SELECT COUNT(*) FROM my_covotes')
#     return cursor.fetchone()[0]  # fetchone always returns tuple
