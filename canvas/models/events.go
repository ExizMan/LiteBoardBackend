package models

type Message struct {
	Type    string      `json:"type"` // draw, undo, clear, insert_text, insert_image
	UserID  string      `json:"userId"`
	BoardID string      `json:"boardId"`
	Payload interface{} `json:"payload"`
}

type DrawPayload struct {
	X         float64 `json:"x"`
	Y         float64 `json:"y"`
	Color     string  `json:"color"`
	Thickness int     `json:"thickness"`
}

type InsertTextPayload struct {
	X     float64 `json:"x"`
	Y     float64 `json:"y"`
	Text  string  `json:"text"`
	Size  int     `json:"size"`
	Color string  `json:"color"`
}

type InsertImagePayload struct {
	X      float64 `json:"x"`
	Y      float64 `json:"y"`
	URL    string  `json:"url"`
	Width  int     `json:"width"`
	Height int     `json:"height"`
}
