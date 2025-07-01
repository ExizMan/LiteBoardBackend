package models

import (
	"time"
	"gorm.io/gorm"
	"encoding/json"
	"errors"
)

type CanvasEvent struct {
	gorm.Model
	BoardID   string    `gorm:"index"` // Для быстрого поиска по доске
	UserID    string    // Кто совершил действие
	Action    string    // Тип события: "draw_line", "move_object" и т.д.
	Data      string    `gorm:"type:jsonb"` // JSON с деталями (координаты, цвет и т.д.)
	CreatedAt time.Time // Когда произошло
}

type Message struct {
	Type   string    `json:"type"` // например, "draw"
	Points []Point   `json:"points"`
	Color  string    `json:"color"`
	Width  float64   `json:"width"`
}

type Point struct {
	X float64 `json:"x"`
	Y float64 `json:"y"`
}

// Интерфейс для всех событий
// Позволяет обрабатывать разные типы событий единообразно
// Например, для фильтрации и сериализации

// CanvasEventData — интерфейс для событий
// Все события должны реализовывать GetType()
type CanvasEventData interface {
	GetType() string
}

// --- DRAW ---
type DrawPayload struct {
	Points    []Point `json:"points"`
	Color     string  `json:"color"`
	Thickness int     `json:"thickness"`
}

type DrawEvent struct {
	Type      string      `json:"type"` // "draw"
	UserID    string      `json:"userId"`
	BoardID   string      `json:"boardId"`
	Payload   DrawPayload `json:"payload"`
	Timestamp int64       `json:"timestamp"`
}

func (e DrawEvent) GetType() string { return e.Type }

// --- CURSOR MOVE ---
type CursorMovePayload struct {
	X     int    `json:"x"`
	Y     int    `json:"y"`
	Email string `json:"email"`
}

type CursorMoveEvent struct {
	Type      string            `json:"type"` // "cursor_move"
	UserID    string            `json:"userId"`
	BoardID   string            `json:"boardId"`
	Payload   CursorMovePayload `json:"payload"`
	Timestamp int64             `json:"timestamp"`
}

func (e CursorMoveEvent) GetType() string { return e.Type }

// --- Универсальный парсер ---
// Определяет тип события и возвращает соответствующую структуру
func ParseCanvasEvent(data []byte) (CanvasEventData, error) {
	var typeHolder struct {
		Type string `json:"type"`
	}
	if err := json.Unmarshal(data, &typeHolder); err != nil {
		return nil, err
	}
	switch typeHolder.Type {
	case "draw":
		var e DrawEvent
		if err := json.Unmarshal(data, &e); err != nil {
			return nil, err
		}
		return e, nil
	case "cursor_move":
		var e CursorMoveEvent
		if err := json.Unmarshal(data, &e); err != nil {
			return nil, err
		}
		return e, nil
	default:
		return nil, errors.New("unknown event type")
	}
}