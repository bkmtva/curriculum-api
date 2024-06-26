import os
from logging import config as logging_config

from src.core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv('PROJECT_NAME', 'Curriculum APIs')

# Настройки Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'redis-1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = 0
# Настройки Elasticsearch
ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_URL = os.getenv('ASYNC_DATABASE_URL')

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
RESET_SECRET_KEY = os.getenv('RESET_SECRET_KEY')
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24
REFRESH_TOKEN_EXPIRE_MINUTES = 120*24
