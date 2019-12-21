import sqlite3
import sys
from functools import wraps

DATABASE_FILE = ':memory:'
conn = sqlite3.connect(DATABASE_FILE)

def query_logger(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("Executing query", *args, file=sys.stderr)
        try:
            return f(*args, **kwargs)
        except sqlite3.Error as e:
            print("SQL Error Occurred:", e.args[0], file=sys.stderr)
    return decorated_function

@query_logger
def execute(query):
    with conn:
        conn.executescript(query)

@query_logger
def fetchone(query):
    with conn:
        return conn.execute(query).fetchone()

@query_logger
def fetchall(query):
    with conn:
        return conn.execute(query).fetchall()

def init_database():
    # Assume for the actual site, you do not know the content of
    # the database as initialized below!
    conn.executescript("""
    CREATE TABLE users (username text PRIMARY KEY UNIQUE NOT NULL, hash text NOT NULL, avatar text NOT NULL, age int NOT NULL);
    
    INSERT INTO users VALUES ('xoxogg', '64762ccf8e701cf9a687c4b9eb4fa88d590a202ff538dcd7d8e9391f53f2df3e', '', 0);
    INSERT INTO users VALUES ('dirks', 'b0dfb38a228cac2fc08bae7a4047f36211f844daffd5b55982c6dc754e5022b7', '/static/images/dirks.jpg', 0);
    
    CREATE TABLE sessions (id uuid PRIMARY KEY UNIQUE NOT NULL, username text NOT NULL);
    INSERT INTO sessions VALUES ('a1bb809d940217cd6866df4b8e349b356a7ec4883faaeb87752a4d4fcb080558612cef59371f6d1d410cf8a459', 'dirks');

    CREATE TABLE posts (username text NOT NULL, post text NOT NULL);
    INSERT INTO posts VALUES ('dirks', 'Caltopia rules the land!');
    INSERT INTO posts VALUES ('dirks', 'does carol srsly think she can misuse public funds as well as me??? lmao');
    """)
    conn.commit()

init_database()
