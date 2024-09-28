## v0.4.0 (2024-09-28)

### Feat

- Implement basic webcrawler for chat API

### Fix

- Add new chat Ninja API
- Format import sorting using ruff
- Add bs4 dependency
- Implement basic chatroom API
- Update migrations style
- Implement basic bot, and AI model API
- Update bot index
- Add owner field to bot model and add bot_id to index
- Add role_id to Message model and update the role field using enum value
- Add bot model
- Add modality and timestamp for each bot model
- Add unique uuid to chat models
- Replace model with vendor from API Key model

## v0.3.1 (2024-09-16)

### Fix

- Enhance consumer logger for error logging
- Chat admin page

## v0.3.0 (2024-09-16)

### Feat

- Init application architecture refactory

### Fix

- Update unit-test
- Rename Chat model to Message model
- Integrate OpenAI Client from shz-llm-client
- Integrate shz-llm-client
- Fix legacy unit-test for new user model
- Implement basic whoami api
- Init basic member unit-test
- Init basic signup and logout api
- Init basic login view with Django Ninja
- Update docker file for building psycopy2
- Add dependency for django-ninja
- Add uuid field for AI vendor and model
- Add ipython to dev dependencies
- Update uv.lock
- Update venv settings

## v0.2.0 (2024-09-02)

### Feat

- **chat**: Add simple sign up view

### Fix

- Upgrade python image version to 3.11
- Update file related to uv
- Init git pre-commit config
- Init pyproject.toml
- Update model
- **chat**: Reset default modelId to gpt-3.5-turbo
- **consumer**: Resolve duplicated message broadcasting

## v1.0.1-beta (2023-06-29)

## v1.0.0-beta (2023-06-28)

## v0.1.0-alpha (2023-06-28)
