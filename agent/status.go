package agent

import (
	"time"
)

type Status struct {
	StatusText           string     `json:"status_text"`
	StatusEmoji          string     `json:"status_emoji"`
	StatusExpiration     *int64     `json:"status_expiration,omitempty"`
	StatusExpirationTime *time.Time `json:"status_expiration_time,omitempty"`
	Disturb              bool       `json:"disturb"`
}
