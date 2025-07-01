package hub

import (
	"canvas/models"
	"encoding/json"
	"github.com/gorilla/websocket"
	"log"
	"sync"
)

type Client struct {
	UserID string
	Conn   *websocket.Conn
}

type BoardSession struct {
	Clients []*Client
	// History []models.Message
	Mutex   sync.Mutex
}

var (
	boards = make(map[string]*BoardSession)
	mu     sync.Mutex
)

func RegisterClient(boardId, userId string, conn *websocket.Conn) {
	log.Printf("Registering client: userId=%s, boardId=%s", userId, boardId)
	mu.Lock()
	session, ok := boards[boardId]
	if !ok {
		session = &BoardSession{}
		boards[boardId] = session
	}

	session.Mutex.Lock()
	session.Clients = append(session.Clients, &Client{UserID: userId, Conn: conn})
	session.Mutex.Unlock()
	mu.Unlock()

	go listen(conn, boardId, userId)
}

// func listen(conn *websocket.Conn, boardId, userId string) {
// 	for {
// 		_, msg, err := conn.ReadMessage()
// 		if err != nil {
// 			break
// 		}

// 		var parsed models.Message
// 		if err := json.Unmarshal(msg, &parsed); err == nil {
// 			mu.Lock()
// 			session := boards[boardId]
// 			session.Mutex.Lock()
// 			session.History = append(session.History, parsed)
// 			session.Mutex.Unlock()
// 			mu.Unlock()
// 		}

// 		broadcast(boardId, msg, userId)
// 	}
// }


func listen(conn *websocket.Conn, boardID, userID string) {
	defer conn.Close()
	log.Printf("Listening websocket: userId=%s, boardId=%s", userID, boardID)
	for {
		_, msg, err := conn.ReadMessage()
		if err != nil {
			log.Printf("WebSocket read error: %v (userId=%s, boardId=%s)", err, userID, boardID)
			break
		}
		var parsed models.Message
		// if err := json.Unmarshal(msg, &parsed); err == nil {
			// log.Printf("Received message: type=%s, userId=%s, boardId=%s", parsed.Type, userID, boardID)
		// }
		broadcast(boardID, msg, userID)
	}
}

func broadcast(boardId string, msg []byte, senderId string) {
	// log.Printf("Broadcasting message: boardId=%s, senderId=%s", boardId, senderId)

	// Используем универсальный парсер для определения типа события
	event, err := models.ParseCanvasEvent(msg)
	if err == nil {
		if event.GetType() == "draw" {
			// Только draw сохраняем в Redis
			var parsed models.Message
			_ = json.Unmarshal(msg, &parsed) // для совместимости с сигнатурой saveToRedis
			saveToRedis(boardId, senderId, parsed, msg)
		}
	}
	mu.Lock()
	session := boards[boardId]
	session.Mutex.Lock()
	defer session.Mutex.Unlock()
	// log.Printf("MSG: %s", msg)
	defer mu.Unlock()
	for _, client := range session.Clients {
		if client.UserID != senderId {
			err := client.Conn.WriteMessage(websocket.TextMessage, msg)
			if err != nil {
				log.Printf("WebSocket send error: %v (to userId=%s, boardId=%s)", err, client.UserID, boardId)
			}
		}
	}
}
