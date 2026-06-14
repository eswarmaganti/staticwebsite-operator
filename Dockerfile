# Base image -- lightweigh python on Alpine Linux
FROM python:3.12-alpine

# The image metadata
LABEL CREATED_BY="Eswar Krishna Maganti"
LABEL CREATOR_MAIL="maganti.ek@gmail.com"
LABEL PROJECT="staticwebsite-operator"
LABEL VERSION="v1alpha1"

# The Build Arguments - UID/GID/username are overridable at build tome
ARG APP_UID=1000
ARG APP_GID=1000
ARG APP_USER=app

# Python runtime configuration

# lets python resolve the sw_operator package
ENV PYTHONPATH="/app"
# ensure log stream in realtime (no bufferring)
ENV PYTHONUNBUFFERED=1
# prevents __pycache__ creatin inside the image
ENV PYTHONDONTWRITEBYTECODE=1

# Create a non-root user and group for running the operator
RUN addgroup -g ${APP_GID} ${APP_USER} && \
    adduser -D -H -u ${APP_UID} -G ${APP_USER} ${APP_USER}

WORKDIR /app

#  Copy dependencies first -- before application code
# This ensures Docker caches this layer separetely, so pop install
# only re-runs when requirements.txt chnages, not on every code change
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code and assign ownership to the app user
COPY sw_operator ./sw_operator
RUN chown -R ${APP_USER}:${APP_USER} /app

# Drop to non-root user before runtime
USER ${APP_USER}

# Run the operator controller using kopf
CMD [ "kopf", "run", "-m", "sw_operator.main", "--all-namespaces" ]