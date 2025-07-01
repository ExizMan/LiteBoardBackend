package models

import (
	"time"
	"gorm.io/gorm"
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