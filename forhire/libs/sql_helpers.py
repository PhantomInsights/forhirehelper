"""DB Helpers that abstract SQL queries."""

import sqlite3


def init_db():
    """Creates a database if it doesn't exist."""

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    create_tables(cursor)
    return conn


def create_tables(cursor):
    """Creates the tables."""

    keywords_query = """CREATE TABLE IF NOT EXISTS keywords (word TEXT UNIQUE)"""
    blacklist_query = """CREATE TABLE IF NOT EXISTS blacklist (word TEXT UNIQUE)"""
    posts_query = """CREATE TABLE IF NOT EXISTS posts (post_id TEXT UNIQUE,
        author TEXT, title TEXT, link TEXT, selftext TEXT, pub_date TEXT) """

    cursor.execute(keywords_query)
    cursor.execute(blacklist_query)
    cursor.execute(posts_query)


def insert_word_to_table(conn, table_name, value):
    """Inserts a word to the specified table."""

    with conn:
        query = "INSERT INTO {} VALUES (?)".format(table_name)
        conn.execute(query, (value,))


def delete_word_from_table(conn, table_name, value):
    """Deletes a word from the specified table."""

    with conn:
        query = "DELETE FROM {} WHERE word=?".format(table_name)
        conn.execute(query, (value,))


def load_words(conn, table_name):
    """Returns the values  from the specified table."""

    with conn:
        query = "SELECT * FROM {} ORDER BY word ASC".format(table_name)
        return conn.execute(query)


def insert_post_to_table(conn, data_dict):
    """Inserts a post to the posts table."""

    with conn:
        query = "INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?)"
        conn.execute(query, (data_dict["post_id"], data_dict["author"], data_dict["title"],
                             data_dict["link"], data_dict["text"], data_dict["pub_date"]))


def delete_post_from_table(conn, value):
    """Deletes a post from the posts table."""

    with conn:
        query = "DELETE FROM posts WHERE post_id=?"
        conn.execute(query, (value,))


def load_posts(conn):
    """Returns all the posts from the posts table."""

    with conn:
        query = "SELECT * FROM posts"
        return conn.execute(query)
