FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Avoid interactive prompts during image build
ENV DEBIAN_FRONTEND=noninteractive

# Install only essentials required before Conda is available
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        git \
        libffi-dev \
        libssl-dev \
        pkg-config \
        unzip \
        wget \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda and set up the base paths
ARG MINICONDA_VERSION=py313_25.9.1-3
ARG MINICONDA_INSTALLER=Miniconda3-${MINICONDA_VERSION}-Linux-x86_64.sh
ENV CONDA_DIR=/opt/conda
RUN curl -fsSL https://repo.anaconda.com/miniconda/${MINICONDA_INSTALLER} -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -b -p ${CONDA_DIR} \
    && rm /tmp/miniconda.sh \
    && ${CONDA_DIR}/bin/conda clean -afy

# Copy dependency specifications
COPY .devcontainer/environment.yml /tmp/environment.yml
COPY .devcontainer/requirements.txt /tmp/pip-requirements.txt

# Create the mcdia environment with the required Python version and install dependencies
ARG PYTHON_VERSION=3.13
RUN ${CONDA_DIR}/bin/conda update -y -n base -c defaults conda \
    && sed -i "s/PYTHON_VERSION_PLACEHOLDER/${PYTHON_VERSION}/" /tmp/environment.yml \
    && ${CONDA_DIR}/bin/conda env create -f /tmp/environment.yml \
    && rm /tmp/environment.yml /tmp/pip-requirements.txt \
    && ${CONDA_DIR}/bin/conda clean -afy

# Make the environment active by default
ENV PATH=${CONDA_DIR}/envs/mcdia/bin:${CONDA_DIR}/bin:${PATH}
ENV CONDA_DEFAULT_ENV=mcdia
