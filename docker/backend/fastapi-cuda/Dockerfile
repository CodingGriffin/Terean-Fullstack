# syntax=docker.io/docker/dockerfile:1.7-labs
#FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu24.04
FROM nvidia/cuda:12.6.3-cudnn-devel-ubuntu24.04

EXPOSE 5000

# NEED TO MAKE SURE CUDA VERSION IS COMPATIBLE WITH HARDWARE

# Install python 3.13 + Dependencies
RUN apt update -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install software-properties-common build-essential libffi-dev -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt install python3.13 python3.13-dev -y
RUN apt install curl wget git -y
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.13 get-pip.py
RUN python3.13 -m pip install --upgrade pip

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

# Install Pycuda
ENV PATH="/usr/local/cuda-12.8/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/cuda-12.8/lib64:${LD_LIBRARY_PATH}"
ENV LD_LIBRARY_PATH="/usr/local/cuda-12.8/compat/:${LD_LIBRARY_PATH}"
ENV CPATH="/usr/local/cuda-12.8/targets/x86-64-linux/include:${CPATH}"
ENV LIBRARY_PATH="/usr/local/cuda-12.8/targets/x86-64-linux/lib:${LIBRARY_PATH}"
RUN pip install pycuda --root-user-action=ignore

# Install requirements
COPY backend/requirements.txt .

RUN pip install -r requirements.txt

# Copy over backend code
COPY --exclude="settings/secret" --exclude=".venv" backend backend/

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5050"]
