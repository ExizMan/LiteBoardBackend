package handlers

import (
	"context"
	"net/http"
	"time"
	"log"

	handwritingpb "canvas/handwriting"
	"github.com/gin-gonic/gin"
	"google.golang.org/grpc"
)

type DrawEvent struct {
	Type      string      `json:"type"`
	UserID    string      `json:"userId"`
	BoardID   string      `json:"boardId"`
	Payload   DrawPayload `json:"payload"`
	Timestamp int64       `json:"timestamp"`
}

type DrawPayload struct {
	Points    []Point `json:"points"`
	Color     string  `json:"color"`
	Thickness int     `json:"thickness"`
}

type Point struct {
	X float64 `json:"x"`
	Y float64 `json:"y"`
}

func RecogniseHandwriting(c *gin.Context) {
	log.Println("[recognise] Новый JSON-запрос на распознавание (draw events)")
	var events []DrawEvent
	if err := c.ShouldBindJSON(&events); err != nil {
		log.Printf("[recognise][error] Не удалось распарсить JSON: %v", err)
		c.JSON(http.StatusBadRequest, gin.H{"error": "Некорректный JSON"})
		return
	}
	log.Printf("[recognise] Получено событий: %d", len(events))

	// Преобразуем в protobuf
	pbEvents := make([]*handwritingpb.DrawEvent, 0, len(events))
	for _, e := range events {
		points := make([]*handwritingpb.Point, 0, len(e.Payload.Points))
		for _, p := range e.Payload.Points {
			points = append(points, &handwritingpb.Point{X: p.X, Y: p.Y})
		}
		pbEvents = append(pbEvents, &handwritingpb.DrawEvent{
			Type:      e.Type,
			UserId:    e.UserID,
			BoardId:   e.BoardID,
			Payload: &handwritingpb.DrawPayload{
				Points:    points,
				Color:     e.Payload.Color,
				Thickness: int32(e.Payload.Thickness),
			},
			Timestamp: e.Timestamp,
		})
	}

	log.Println("[recognise] Подключаюсь к gRPC сервису mlrecogniser:50051")
	conn, err := grpc.Dial("mlrecogniser:50051", grpc.WithInsecure(), grpc.WithBlock(), grpc.WithTimeout(2*time.Second))
	if err != nil {
		log.Printf("[recognise][error] Не удалось подключиться к gRPC сервису: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Не удалось подключиться к сервису распознавания"})
		return
	}
	defer conn.Close()

	client := handwritingpb.NewHandwritingRecognizerClient(conn)
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	log.Println("[recognise] Отправляю события на gRPC сервис")
	resp, err := client.Recognize(ctx, &handwritingpb.HandwritingRequest{Events: pbEvents})
	if err != nil {
		log.Printf("[recognise][error] Ошибка при вызове gRPC: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Ошибка при распознавании текста"})
		return
	}
	log.Printf("[recognise] gRPC ответ: сглажено событий %d", len(resp.Events))
	
	c.JSON(http.StatusOK, gin.H{"events": resp.Events})} 