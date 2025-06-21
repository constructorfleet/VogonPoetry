FROM python:3.10-slim

RUN apt-get update

# Get Ubuntu packages
RUN apt-get install -y \
    build-essential \
    curl

# Update new packages
RUN apt-get update

# Get Rust
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y

RUN echo 'source $HOME/.cargo/env' >> $HOME/.bashrc
RUN echo 'source $HOME/.cargo/env' >> $HOME/.bashrc
RUN pip install poetry

WORKDIR /workspace