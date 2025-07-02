package main

import (
	"canvas/config"
	"canvas/handlers"
	"canvas/hub"
	"canvas/models"
	"github.com/gin-gonic/gin"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"log"
	"time"
)

// CORS middleware
func CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")
		c.Header("Access-Control-Allow-Credentials", "true")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}

func main() {
	config.LoadConfig()
	log.Println("Starting server...")
	hub.InitRedis(config.Cfg.RedisAddr)

	// Если окружение dev — очищаем все canvas:* стримы в Redis
	if config.Cfg.Env == "dev" {
		log.Println("[DEV] Clearing all canvas streams in Redis...")
		hub.ClearAllCanvasStreams()
	}

	db, err := gorm.Open(postgres.Open(config.Cfg.PostgresDSN), &gorm.Config{})
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	db.AutoMigrate(&models.CanvasEvent{})

	interval, err := time.ParseDuration(config.Cfg.SyncInterval)
	if err != nil {
		log.Fatalf("Invalid sync_interval in config: %v", err)
	}
	log.Printf("Starting sync worker, interval: %v", interval)
	go hub.StartSyncWorker(db, interval)

	r := gin.Default()
	
	// Добавляем CORS middleware
	r.Use(CORSMiddleware())
	
	r.GET("/canvas/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "pong"})
	})
	r.GET("/canvas/ws/:boardId", func(c *gin.Context) {
		c.Set("db", db)
		handlers.HandleWebSocket(c)
	})
	r.POST("/canvas/recognise", handlers.RecogniseHandwriting)
	log.Printf("Server running on port %s", config.Cfg.Port)
	r.Run(":" + config.Cfg.Port)
}
