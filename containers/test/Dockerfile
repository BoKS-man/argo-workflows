FROM python:3.8-slim
WORKDIR /workspace/app
COPY . /workspace/app
RUN pip install numpy torch
ENTRYPOINT [ "python", "./run.py"]