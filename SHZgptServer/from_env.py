import os
import ast

# General Settings
APP_NAME = os.environ.get('APP_NAME', 'blog')
DEPLOY_STAGE = os.environ.get('DEPLOY_STAGE', 'local')
IS_DEBUG = (os.environ.get('IS_DEBUG', 'True') == 'True')

# SECURITY WARNING: keep the secret key used in production secret!
DJANGO_SECRET_KEY=os.environ.get('DJANGO_SECRET_KEY', 'you_should_generate_new_key')
CORS_ALLOWED_ORIGIN=os.environ.get('CORS_ALLOWED_ORIGIN', '["http://127.0.0.1:3000"]')
try:
    CORS_ALLOWED_ORIGIN = ast.literal_eval(CORS_ALLOWED_ORIGIN)
    if not isinstance(CORS_ALLOWED_ORIGIN, list):
        raise ValueError("CORS_ALLOWED_ORIGIN should be a valid Python list string representation")
except ValueError:
    raise ValueError("CORS_ALLOWED_ORIGIN should be a valid Python list string representation")

COOKIES_ALLOWED_DOMAIN=os.environ.get('COOKIES_ALLOWED_DOMAIN', '.127.0.0.1')

# Container Settings
IN_CONTAINER = os.environ.get('IN_CONTAINER', False)
if IN_CONTAINER:
    CONTAINER_STORAGE_PATH = os.environ.get('CONTAINER_STORAGE_PATH', '')
    LOGGING_FILE_NAME = os.environ.get('LOGGIN_FILE_NAME', 'app.log')

DJANGO_ADMIN_URL_PATH = os.environ.get('DJANGO_ADMIN_URL_PATH', 'admin/')

# Database Settings
DATABASE_DB_NAME = os.environ.get('DATABASE_DB_NAME', 'for-development')
DATABASE_USER = os.environ.get('DATABASE_USER', 'devel')
DATABASE_PASSWD = os.environ.get('DATABASE_PASSWD', 'for-development')
DATABASE_URI = os.environ.get('DATABASE_URI', 'localhost')
DATABASE_READ_URI = os.environ.get('DATABASE_READ_URI', 'localhost')
DATABASE_URI_PORT = os.environ.get('DATABASE_URI_PORT', 5432)

# S3 Settings
AWS_S3_REGION = os.environ.get('AWS_S3_REGION')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': f'max-age={os.environ.get("AWS_S3_CACHE_CONTROL_MAX_AGE")}',
}
AWS_LOCATION = 'django'
