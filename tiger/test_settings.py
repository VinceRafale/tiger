from tiger.common_settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'test_tiger'             # Or path to database file if using sqlite3.
DATABASE_USER = 'tiger'             # Not used with sqlite3.
DATABASE_PASSWORD = 'tiger'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

HAYSTACK_WHOOSH_PATH = '/home/jonathan/mysite_index'

CACHE_BACKEND = 'redis_cache.cache://127.0.0.1:6379'
