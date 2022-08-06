FROM ubuntu:focal

RUN apt update
RUN apt install -y python3 python3-pip lsb-release
RUN apt install -y sudo
RUN apt clean

RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo


RUN mkdir /app
WORKDIR /app
COPY . /app
CMD ["bash"]
