FROM python:3.11-slim

WORKDIR /app

COPY mlrecogniser/requirements.txt ./
COPY mlrecogniser/ .
RUN pip install --no-cache-dir -r requirements.txt


COPY canvas/handwriting.proto ./

RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. handwriting.proto

CMD ["python", "handwriting_service.py"] 