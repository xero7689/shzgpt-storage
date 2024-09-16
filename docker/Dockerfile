FROM python:3.11.10-slim AS build-image

RUN apt-get --allow-releaseinfo-change update && apt-get install -y git libpq-dev gcc

RUN apt-get clean autoclean && apt-get autoremove --yes && rm -rf /var/lib/{apt,dpkg,cache,log}/

ARG GIT_USER
ARG GIT_PASSWORD
RUN git config --global credential.helper store
RUN echo "https://${GIT_USER}:${GIT_PASSWORD}@gitlab.com" >> /root/.git-credentials

COPY requirements.txt .
RUN pip install -r requirements.txt -t /python_package

ARG IS_DEBUG
ENV IS_DEBUG=$IS_DEBUG
COPY requirements-dev.txt .
RUN if [ "$IS_DEBUG" = "True" ] ; then pip install -r requirements-dev.txt -t /python_package ; fi


FROM python:3.11.10-slim AS deploy-image
COPY --from=build-image /python_package /python_package

# Install necessary PostgreSQL library
RUN apt-get --allow-releaseinfo-change update && apt-get install -y libpq-dev

# Environment for Python
ENV PATH=/python_package/bin:$PATH
ENV PYTHONPATH=/python_package/:$PYTHONPATH

# Environemnt for Django Admin
ARG DJANGO_SUPERUSER_USERNAME
ARG DJANGO_SUPERUSER_PASSWORD
ARG DJANGO_SUPERUSER_EMAIL
ENV DJANGO_SUPERUSER_USERNAME=$DJANGO_SUPERUSER_USERNAME
ENV DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD
ENV DJANGO_SUPERUSER_EMAIL=$DJANGO_SUPERUSER_EMAIL

# WorkSpace Settings
WORKDIR /workspace

COPY . .
ENTRYPOINT /bin/bash docker/bin/startup.sh $DJANGO_SUPERUSER_USERNAME $DJANGO_SUPERUSER_PASSWORD $DJANGO_SUPERUSER_EMAIL
