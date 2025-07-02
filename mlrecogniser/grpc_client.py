import grpc
import handwriting_pb2
import handwriting_pb2_grpc

def recognise_image(image_bytes, host="localhost", port=50051):
    channel = grpc.insecure_channel(f"{host}:{port}")
    stub = handwriting_pb2_grpc.HandwritingRecognizerStub(channel)
    request = handwriting_pb2.HandwritingRequest(image=image_bytes)
    response = stub.Recognize(request)
    return response.text

if __name__ == "__main__":
    # Пример: читаем картинку из файла
    with open("test_image.png", "rb") as f:
        img_bytes = f.read()
    text = recognise_image(img_bytes)
    print("Распознанный текст:", text) 