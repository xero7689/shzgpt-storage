FROM python:3.9.10 AS build-image

RUN apt-get --allow-releaseinfo-change update && apt-get install -y git

RUN apt-get clean autoclean && apt-get autoremove --yes && rm -rf /var/lib/{apt,dpkg,cache,log}/

ARG GIT_USER
ARG GIT_PASSWORD
RUN git config --global credential.helper store
RUN echo "https://${GIT_USER}:${GIT_PASSWORD}@gitlab.com" >> /root/.git-credentials

COPY requirements.txt .
RUN pip install -r requirements.txt -t /python_package

FROM python:3.9.10 AS deploy-image
COPY --from=build-image /python_package /python_package

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
CMD python manage.py runserver 0.0.0.0:8000
