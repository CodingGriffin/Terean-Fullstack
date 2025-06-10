# syntax=docker.io/docker/dockerfile:1.7-labs
#FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04
#FROM nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04
FROM nvidia/cuda:11.6.2-cudnn8-devel-ubuntu20.04

EXPOSE 8000

# NEED TO MAKE SURE CUDA VERSION IS COMPATIBLE WITH HARDWARE

# Install python 3.13 + Dependencies
RUN apt update -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install software-properties-common build-essential libffi-dev -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt install python3.13 python3.13-dev -y
RUN apt install curl wget git python-six -y
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.13 get-pip.py
RUN python3.13 -m pip install --upgrade pip

WORKDIR /app

# Install terean core from github
# One command, so keys go away after container is built
RUN --mount=type=bind,source=backend/src/settings,target=/container_readonly_data,readonly \
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

# Install Pycuda
RUN pip install pycuda --root-user-action=ignore

# Install requirements
COPY backend/requirements.txt .

RUN pip install -r requirements.txt

# I don't know why, but it works if this is here?
RUN pip uninstall six -y
RUN pip install six

# Copy over backend code
COPY --exclude="settings/secret" --exclude=".venv" backend backend/

WORKDIR /app/backend/src

#CMD ["nvidia-smi"]
#CMD ["sleep", "infinity"]
CMD ["uvicorn", "main:app", "--proxy-headers", "--forwarded-allow-ips=*", "--host", "0.0.0.0", "--port", "8000"]
