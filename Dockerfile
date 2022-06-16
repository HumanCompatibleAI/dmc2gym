# Adapted from HumanCompatileAI/imitation, based on OpenAI's mujoco-py Dockerfile

# base stage contains just binary dependencies.
# This is used in the CI build.
FROM nvidia/cuda:11.6.2-cudnn8-runtime-ubuntu18.04 AS base
ARG DEBIAN_FRONTEND=noninteractive

# add-apt-repository is needed before installing latest Python
# software-properties-common should be installed before add-apt-repository
RUN apt-get update -q \
    && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa

RUN apt-get update -q \
    && apt-get install -y --no-install-recommends \
    # Install latest Python3.9
    python3.9 \
    python3.9-dev \
    python3.9-distutils \
    python3-pip \
    build-essential \
    # Used by mujoco211
    wget \
    git \
    # libgl1-mesa-dev \
    libgl1-mesa-glx \
    # libglew-dev \
    libosmesa6 \
    net-tools \
    unzip \
    vim \
    virtualenv \
    xpra \
    xserver-xorg-dev \
    # For OpenGL rendering backend (for dm_control) 
    libglfw3 \
    libglew2.0 \
    # Other tools to make life easier
    tmux \
    patchelf  \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV LANG C.UTF-8

# dm_control uses mujoco211
RUN mkdir -p /root/.mujoco \
    && wget -P /root/.mujoco/ "https://github.com/deepmind/mujoco/releases/download/2.1.1/mujoco-2.1.1-linux-x86_64.tar.gz" \
    && tar -zxvf /root/.mujoco/mujoco-2.1.1-linux-x86_64.tar.gz --no-same-owner -C /root/.mujoco/ \
    && rm /root/.mujoco/mujoco-2.1.1-linux-x86_64.tar.gz

# Specify path/to/libmujoco211.so (for dm_control)
ENV MJLIB_PATH=/root/.mujoco/mujoco-2.1.1/lib/libmujoco.so.2.1.1

# Run Xdummy mock X server by default so that rendering will work.
COPY ci/xorg.conf /etc/dummy_xorg.conf
COPY ci/Xdummy-entrypoint.py /usr/bin/Xdummy-entrypoint.py
ENTRYPOINT ["/usr/bin/Xdummy-entrypoint.py"]

# python-req stage contains Python venv, but not code.
# It is useful for development purposes: you can mount
# code from outside the Docker container.
# CircleCI needs an empty working directory to checkout
WORKDIR /dmc2gym
FROM base as dev

# Copy only necessary dependencies to build virtual environment.
# This minimizes how often this layer needs to be rebuilt.
COPY ./setup.py ./setup.py
COPY ci/build_venv.sh ./ci/build_venv.sh
# COPY ./pyproject.toml ./pyproject.toml
RUN mkdir src

# Build virtual environment
# RUN /dmc2gym/ci/build_venv.sh /venv
RUN ci/build_venv.sh /venv \
    && rm -rf $HOME/.cache/pip

# Full stage contains everything.
# Can be used for deployment and local testing.
FROM dev as full

# # Delay copying (and installing) the code until the very end
# COPY . /dmc2gym
# # Build a wheel then install to avoid copying whole directory (pip issue #2195)
# RUN python setup.py sdist bdist_wheel
# RUN pip install --upgrade --no-deps dist/dmc2gym-*.whl

# # Default entrypoints
# CMD ["pytest", "-n", "auto", "-vv", "tests/""]
