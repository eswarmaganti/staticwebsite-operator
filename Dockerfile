# the base image for the operator
FROM python:3.12-alpine

# The image metadata
LABEL CREATED_BY="Eswar Krishna Maganti"
LABEL CREATOR_MAIL="maganti.ek@gmail.com"
LABEL PROJECT="staticwebsite-operator"
LABEL VERSION="v1alpha1"

# The Arguments
ARG APP_UID=1000
ARG APP_GID=1000
ARG APP_USER=app

# setting the PYTHONPATH to project working dir
ENV PYTHONPATH="/app"

# For enabling the real-time logs
ENV PYTHONUNBUFFERED=1

# Avoids creating the __pycache__
ENV PYTHONDONTWRITEBYTECODE=1

# creating the group and user
RUN addgroup -g ${APP_GID} ${APP_USER} && \
    adduser -D -H -u ${APP_UID} -G ${APP_USER} ${APP_USER}

WORKDIR /app

# copy the dependency file and install python dependencies
COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# copy the application code
COPY sw_operator ./sw_operator
RUN chown -R ${APP_USER}:${APP_USER} /app

# switch to application user
USER ${APP_USER}

CMD [ "kopf", "run", "-m", "sw_operator.main", "--all-namespaces" ]