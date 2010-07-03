from tiger.common_settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'tiger'             # Or path to database file if using sqlite3.
DATABASE_USER = 'tiger_dba'             # Not used with sqlite3.
DATABASE_PASSWORD = 'MAAANNNIIING'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

HAYSTACK_SEARCH_ENGINE = 'solr'
HAYSTACK_SOLR_URL = 'http://10.176.224.6:8080/solr'

CACHE_BACKEND = 'redis_cache.cache://10.176.225.139:6379'
