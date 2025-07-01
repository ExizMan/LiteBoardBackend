package handlers

import (
	"canvas/hub"
	"canvas/models"
	"canvas/utils"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"gorm.io/gorm"
	"net/http"
	"log"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

func HandleWebSocket(c *gin.Context) {
	boardId := c.Param("boardId")
	token := c.Query("token")

	userId, err := utils.ValidateToken(token)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
		return
	}

	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		http.Error(c.Writer, "WebSocket upgrade failed", http.StatusBadRequest)
		return
	}

	dbAny, exists := c.Get("db")
	if !exists {
		log.Println("DB not found in context")
		conn.Close()
		return
	}
	db := dbAny.(*gorm.DB)

	// 1. История из БД
	var events []models.CanvasEvent
	err = db.Where("board_id = ?", boardId).Order("created_at asc").Find(&events).Error
	if err != nil {
		log.Printf("DB history error: %v", err)
	}
	for _, event := range events {
		log.Printf("[POSTGRES] Sending event to client: %s", event.Data)
		conn.WriteMessage(websocket.TextMessage, []byte(event.Data))
	}

	// 2. История из Redis
	redisEvents, err := hub.GetBoardHistoryFromRedis(boardId)
	if err != nil {
		log.Printf("Redis history error: %v", err)
	}
	for _, data := range redisEvents {
		log.Printf("[REDIS] Sending event to client: %s", data)
		conn.WriteMessage(websocket.TextMessage, []byte(data))
	}

	hub.RegisterClient(boardId, userId, conn)
}
