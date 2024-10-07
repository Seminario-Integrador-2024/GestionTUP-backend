# define an alias for the specific python version used in this file.
FROM docker.io/python:3.12.5-slim-bookworm AS python

# Python build stage
FROM python AS python-build-stage

ARG BUILD_ENVIRONMENT=local

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg dependencies
  libpq-dev

# Requirements are installed here to ensure they will be cached.
COPY ./requirements .

# Create Python Dependency and Sub-Dependency Wheels.
RUN pip wheel --wheel-dir /usr/src/app/wheels  \
  -r ${BUILD_ENVIRONMENT}.txt


# Python 'run' stage
FROM python AS python-run-stage

ARG BUILD_ENVIRONMENT=local
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV BUILD_ENV=${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}


# devcontainer dependencies and utils
RUN apt-get update && apt-get install --no-install-recommends -y \
  sudo git bash-completion nano ssh

# Create devcontainer user and add it to sudoers
RUN groupadd --gid 1000 dev-user \
  && useradd --uid 1000 --gid dev-user --shell /bin/bash --create-home dev-user \
  && echo dev-user ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/dev-user \
  && chmod 0440 /etc/sudoers.d/dev-user


# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # Install cron
  cron \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
  && rm -rf /wheels/

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# copy application code to WORKDIR
COPY . ${APP_HOME}


# Configurar el crontab para ejecutar el script Python cada minuto
RUN (crontab -l 2>/dev/null; echo "0 0 * * * APP_HOME=${APP_HOME} && PYTHONPATH=${APP_HOME} DJANGO_SETTINGS_MODULE=config.settings.local DATABASE_URL=\$(grep DATABASE_URL ${APP_HOME}/.envs/.local/.postgres | cut -d '=' -f2 | tr -d ' ') USE_DOCKER=yes /usr/local/bin/python ${APP_HOME}/server/tareas_programadas/actualizar_cuotas.py >> ${APP_HOME}/server/tareas_programadas/actualizar_cuotas.log 2>&1") | crontab -


# Asegúrate de que el script tenga permisos de ejecución
RUN chmod +x ${APP_HOME}/server/tareas_programadas/actualizar_cuotas.py

# Run the command on container startup
CMD ["bash", "-c", "service restart cron && tail -f ${APP_HOME}/server/tareas_programadas/actualizar_cuotas.log"]



ENTRYPOINT ["/entrypoint"]
