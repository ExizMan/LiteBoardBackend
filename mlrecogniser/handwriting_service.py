import grpc
from concurrent import futures
import time
import handwriting_pb2
import handwriting_pb2_grpc
from trajectory_smoother import get_trajectory_processor

class HandwritingRecognizerServicer(handwriting_pb2_grpc.HandwritingRecognizerServicer):
    def __init__(self):
        # Инициализируем процессор траекторий при создании сервиса
        self.trajectory_processor = get_trajectory_processor()
    
    def Recognize(self, request, context):
        print(f"Получено событий draw: {len(request.events)}")
        new_events = []
        
        for i, event in enumerate(request.events):
            print(f"Обрабатываю событие {i+1}/{len(request.events)}, точек: {len(event.payload.points)}")
            
            # Применяем нейронную сеть для сглаживания
            smoothed_points = self.trajectory_processor.smooth_trajectory(event.payload.points)
            
            print(f"Событие {i+1}: {len(event.payload.points)} -> {len(smoothed_points)} точек")
            
            new_payload = handwriting_pb2.DrawPayload(
                points=smoothed_points,
                color=event.payload.color,
                thickness=event.payload.thickness
            )
            new_event = handwriting_pb2.DrawEvent(
                type=event.type,
                user_id=event.user_id,
                board_id=event.board_id,
                payload=new_payload,
                timestamp=event.timestamp
            )
            new_events.append(new_event)
        
        print(f"Обработано событий: {len(new_events)}")
        return handwriting_pb2.HandwritingResponse(events=new_events)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    handwriting_pb2_grpc.add_HandwritingRecognizerServicer_to_server(
        HandwritingRecognizerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC сервер для рукописного текста запущен на порту 50051")
    print("Используется нейронная сеть Conv1D для сглаживания траекторий")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve() 