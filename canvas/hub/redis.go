package hub

import (
	"context"
	"log"
	"strings"
	"time"

	"github.com/redis/go-redis/v9"
	"gorm.io/gorm"
	"canvas/models"
)

var (
	rdb *redis.Client
	ctx = context.Background()
	// Разрешённые типы событий для сохранения в БД
	allowedEventTypes = map[string]struct{}{
		"draw": {},
		// "shape": {},
		// "image": {},
	}
)

// Инициализация Redis
func InitRedis(addr string) {
	rdb = redis.NewClient(&redis.Options{
		Addr: addr, // "localhost:6379"
	})
}

// Сохраняет событие в Redis Stream
func saveToRedis(boardID, userID string, msg models.Message, rawMsg []byte) {
	log.Printf("[REDIS] XAdd: boardID=%s, userID=%s, action=%s, data=%s", boardID, userID, msg.Type, string(rawMsg))
	event := map[string]interface{}{
		"user_id": userID,
		"action":  msg.Type, // "draw_line", "add_object" и т.д.
		"data":    string(rawMsg),
	}

	_, err := rdb.XAdd(ctx, &redis.XAddArgs{
		Stream: "canvas:" + boardID,
		Values: event,
	}).Result()

	if err != nil {
		log.Printf("[REDIS][ERROR] XAdd: %v", err)
	}
}

// Запускает фоновую синхронизацию с БД
func StartSyncWorker(db *gorm.DB, interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for range ticker.C {
		syncAllBoards(db)
	}
}

// Синхронизирует все доски из Redis в БД
func syncAllBoards(db *gorm.DB) {
	log.Printf("[REDIS] Keys: pattern=canvas:*")
	streamKeys, err := rdb.Keys(ctx, "canvas:*").Result()
	if err != nil {
		log.Printf("[REDIS][ERROR] Keys: %v", err)
		return
	}

	for _, streamKey := range streamKeys {
		boardID := strings.TrimPrefix(streamKey, "canvas:")
		syncBoardToDB(db, boardID)
	}
}

// Переносит события одной доски из Redis в БД
func syncBoardToDB(db *gorm.DB, boardID string) {
	log.Printf("[REDIS] XRange: boardID=%s", boardID)
	events, err := rdb.XRange(ctx, "canvas:"+boardID, "-", "+").Result()
	if err != nil {
		log.Printf("[REDIS][ERROR] XRange: %v", err)
		return
	}

	if len(events) == 0 {
		return
	}

	var dbEvents []models.CanvasEvent
	var idsToDelete []string
	for _, event := range events {
		dataStr, ok := event.Values["data"].(string)
		if !ok {
			continue
		}
		action, ok := event.Values["action"].(string)
		if !ok {
			continue
		}
		if !isAllowedEventType(action) {
			continue // сохраняем только разрешённые типы
		}
		dbEvents = append(dbEvents, models.CanvasEvent{
			BoardID:   boardID,
			UserID:    event.Values["user_id"].(string),
			Action:    action,
			Data:      dataStr,
			CreatedAt: time.Now(),
		})
		idsToDelete = append(idsToDelete, event.ID)
	}

	// Пакетная вставка в PostgreSQL
	if err := db.Create(&dbEvents).Error; err != nil {
		log.Printf("[POSTGRES][ERROR] Insert events: %v", err)
		return
	}
	log.Printf("[POSTGRES] Insert events: boardID=%s, count=%d", boardID, len(dbEvents))

	// Удаляем все обработанные записи из стрима
	if len(idsToDelete) > 0 {
		if _, err := rdb.XDel(ctx, "canvas:"+boardID, idsToDelete...).Result(); err != nil {
			log.Printf("[REDIS][ERROR] XDel: %v", err)
		} else {
			log.Printf("[REDIS] XDel: boardID=%s, deleted=%d", boardID, len(idsToDelete))
		}
	}

	// Если стрим пустой — удаляем ключ
	streamLen, err := rdb.XLen(ctx, "canvas:"+boardID).Result()
	if err == nil && streamLen == 0 {
		_, _ = rdb.Del(ctx, "canvas:"+boardID).Result()
		log.Printf("[REDIS] DEL: boardID=%s (stream is empty)", boardID)
	}
}

// Проверяет, нужно ли сохранять событие этого типа
func isAllowedEventType(eventType string) bool {
	_, ok := allowedEventTypes[eventType]
	return ok
}

func GetBoardHistoryFromRedis(boardID string) ([]string, error) {
	log.Printf("[REDIS] XRange (history): boardID=%s", boardID)
	var result []string
	events, err := rdb.XRange(ctx, "canvas:"+boardID, "-", "+").Result()
	if err != nil {
		return nil, err
	}
	for _, event := range events {
		if dataStr, ok := event.Values["data"].(string); ok {
			result = append(result, dataStr)
		}
	}
	return result, nil
}

// Удаляет все canvas:* стримы из Redis (для dev-окружения)
func ClearAllCanvasStreams() {
	keys, err := rdb.Keys(ctx, "canvas:*").Result()
	if err != nil {
		log.Printf("[REDIS][ERROR] ClearAllCanvasStreams: %v", err)
		return
	}
	if len(keys) == 0 {
		log.Println("[REDIS] No canvas streams to delete.")
		return
	}
	if _, err := rdb.Del(ctx, keys...).Result(); err != nil {
		log.Printf("[REDIS][ERROR] Del in ClearAllCanvasStreams: %v", err)
	} else {
		log.Printf("[REDIS] Cleared %d canvas streams.", len(keys))
	}
}