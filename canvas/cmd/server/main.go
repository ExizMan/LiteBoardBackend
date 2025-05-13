package main

import (
	"canvas/config"
	"canvas/handlers"
	"github.com/gin-gonic/gin"
)

func main() {
	config.LoadConfig()

	r := gin.Default()
	r.GET("/canvas/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "pong"})
	})
	r.GET("/canvas/ws/:boardId", handlers.HandleWebSocket)
	r.Run(":" + config.Cfg.Port)
}
