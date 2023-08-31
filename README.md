# SHZ GPT Storage Server

This is the backend storage server for the [SHZ GPT project](https://github.com/xero7689/shzgpt) - a chat application utilizing an online LLM model. The purpose of this server is to securely store, manage, and organize chatroom data, user data, and prompt data.

## Features
1. User management: implements login/logout functionality for user management.
2. Chatroom and Chat Session management: stores all the chatroom and chat session data coming from the online LLM model.
3. Custom Prompt Management: enables users to manage their own prompts for quicker chat launching.
4. API Key management: stores the API keys that comming from user's AI service vendor.

## Deployment
### Local
Install the requirement files:
```
pip install -r requirements.txt
```

Run the Django migrations using
```
python manage.py migrate
```

And easily start the server by running:
```
python manage.py runserver {LOCAL_HOST_IP}:{PORT}
```

### Docker
If you prefer to use docker, You can use the docker-compose file provided in the project.

#### .env
Since the compose file takes a .env file in the same directory to construct the container environment, you have to set the following variable before you start building the image and launching the container:

- `APP_NAME`: The name of the application.
- `DEPLOY_STAGE`: The deployment stage or environment.
- `IS_DEBUG`: Specifies whether the application is in debug mode or not.
- `DJANGO_SECRET_KEY`: The secret key used by Django for cryptographic signing and should be kept secure.
- `IN_CONTAINER`: Specifies whether the application is running inside a container or not.
- `CONTAINER_STORAGE_PATH`: Represents the storage path within the container.
- `LOGGING_FILE_NAME`: Specifies the name of the log file to which Django logs are written.
- `DATABASE_URI`: Represents the URI or hostname of the database where the application will connect.
- `DATABASE_DB_NAME`: Specifies the name of the database to be used for development purposes.
- `DATABASE_USER`: Specifies the username for the database connection.
- `DATABASE_PASSWD`: Specifies the password for the database connection.
- `DJANGO_SUPERUSER_USERNAME`: Sets the username for the Django superuser.
- `DJANGO_SUPERUSER_PASSWORD`: Sets the password for the Django superuser.
- `DJANGO_SUPERUSER_EMAIL`: Sets the email address for the Django superuser.
- `DJANGO_ADMIN_URL_PATH`: Specifies the custom URL path for the Django admin interface.
- `CORS_ALLOWED_ORIGIN`: Lists the allowed origins for Cross-Origin Resource Sharing (CORS). This variable should be a string of list representation of Python.
- `COOKIES_ALLOWED_DOMAIN`: Specifies the allowed domain for cookies.

#### Docker Deployment
Build the image using:
```
docker-compose build
```

And start the server:
```
docker-compose up
```

The server will also start a postgres database and  should be accessible on 0.0.0.0:8000 defaultly.

You can modify these configuration as you want!
