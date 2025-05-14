# syntax=docker.io/docker/dockerfile:1.7-labs
FROM python:3.13

EXPOSE 5000

WORKDIR /app

# Install terean core from github
# One command, so keys go away after container is built
RUN --mount=type=bind,source=backend/settings,target=/container_readonly_data,readonly \
    mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh && \
    ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts && \
    cp /container_readonly_data/secret/id_rsa ~/.ssh/ && \
    chmod 600 /root/.ssh/id_rsa && \
    pip install git+ssh://git@github.com/dbarnes-terean/terean-core.git && \
    rm -rf /root/.ssh/id_rsa

# Alternate way of including terean core from a local archive for testing
# It was easier for me to just use this method for testing without getting
# into ssh keys.  You just extract terean core to the root of the project.
# COPY tereancore tereancore/

# Install requirements
COPY backend/requirements.txt .

RUN pip install -r requirements.txt

# Copy over backend code
COPY --exclude="settings/secret" --exclude=".venv" backend backend/

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5050"]
