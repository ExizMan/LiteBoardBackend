package hub

import (
	"canvas/models"
	"encoding/json"
	"github.com/gorilla/websocket"
	"sync"
)

type Client struct {
	UserID string
	Conn   *websocket.Conn
}

type BoardSession struct {
	Clients []*Client
	History []models.Message
	Mutex   sync.Mutex
}

var (
	boards = make(map[string]*BoardSession)
	mu     sync.Mutex
)

func RegisterClient(boardId, userId string, conn *websocket.Conn) {
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

func listen(conn *websocket.Conn, boardId, userId string) {
	for {
		_, msg, err := conn.ReadMessage()
		if err != nil {
			break
		}

		var parsed models.Message
		if err := json.Unmarshal(msg, &parsed); err == nil {
			mu.Lock()
			session := boards[boardId]
			session.Mutex.Lock()
			session.History = append(session.History, parsed)
			session.Mutex.Unlock()
			mu.Unlock()
		}

		broadcast(boardId, msg, userId)
	}
}

func broadcast(boardId string, msg []byte, senderId string) {
	mu.Lock()
	session := boards[boardId]
	session.Mutex.Lock()
	defer session.Mutex.Unlock()
	defer mu.Unlock()

	for _, client := range session.Clients {
		if client.UserID != senderId {
			client.Conn.WriteMessage(websocket.TextMessage, msg)
		}
	}
}
