# SHZ GPT Storage Server

This is the backend storage server for the [SHZ GPT project](https://github.com/xero7689/shzgpt) - a chat application utilizing an online LLM model. The purpose of this server is to securely store, manage, and organize chatroom data, user data, and prompt data.

## Features
1. User management: implements login/logout functionality for user management.
2. Chatroom and Chat Session management: stores all the chatroom and chat session data coming from the online LLM model.
3. Custom Prompt Management: enables users to manage their own prompts for quicker chat launching.

## Deployment
This is a Django project and can be launched locally using the `manage.py runserver` command. The project also supports Docker Compose, allowing for the application to run within a Docker container.

### Local Deployment
1. Clone the repository using the `git clone` command.
2. Install the required dependencies listed in `requirements.txt`.
3. Run the Django migrations using the `python manage.py migrate` command.
4. Launch the application using the `python manage.py runserver` command.

### Docker Deployment
1. Install Docker and Docker Compose on your system.
2. Clone the repository using the `git clone` command.
3. Navigate to the application's root directory.
4. Run the following command to build and start the container: `docker-compose up -d`.
5. The application should now be accessible on `http://localhost:8004`.
  - You may modify the port you want in the wsgi.ini file.