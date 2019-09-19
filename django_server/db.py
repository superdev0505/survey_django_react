from django.db import connection


NANO_STRING_LENGTH = 8
SHORT_STRING_LENGTH = 32
IPV6_STRING_LENGTH = 39
MEDIUM_STRING_LENGTH = 64
DEFAULT_STRING_LENGTH = 256
LONG_STRING_LENGTH = 512


def fetch_all(sql, params=None):
    cursor = connection.cursor()

    if params:
        cursor.execute(sql,params)
    else:
        cursor.execute(sql)

    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def fetch_all_flat(sql, params=None):
    cursor = connection.cursor()

    if params:
        cursor.execute(sql,params)
    else:
        cursor.execute(sql)

    return cursor.fetchall()


def fetch_one(sql, params=None):
    data = fetch_all(sql, params=params)
    if len(data):
        return data[0]
    else:
        return None


def execute(sql, params=None):
    cursor = connection.cursor()

    if params:
        cursor.execute(sql,params)
    else:
        cursor.execute(sql)

    cursor.close()