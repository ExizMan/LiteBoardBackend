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

func main() {
	config.LoadConfig()
	log.Println("Starting server...")
	hub.InitRedis(config.Cfg.RedisAddr)
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
	r.GET("/canvas/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "pong"})
	})
	r.GET("/canvas/ws/:boardId", func(c *gin.Context) {
		c.Set("db", db)
		handlers.HandleWebSocket(c)
	})
	log.Printf("Server running on port %s", config.Cfg.Port)
	r.Run(":" + config.Cfg.Port)
}
