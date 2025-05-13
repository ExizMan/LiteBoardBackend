package handlers

import (
	"canvas/hub"
	"canvas/utils"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"net/http"
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

	hub.RegisterClient(boardId, userId, conn)
}
