from tiger.common_settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'tiger'             # Or path to database file if using sqlite3.
DATABASE_USER = 'tiger_dba'             # Not used with sqlite3.
DATABASE_PASSWORD = 'MAAANNNIIING'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

HAYSTACK_WHOOSH_PATH = '/home/threadsafe/whoosh_index'
