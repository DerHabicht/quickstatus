package agent

import (
	"github.com/nlopes/slack"
)

type Agent struct {
	*slack.Client
}

func New(token string) Agent {
	return Agent{
		slack.New(token),
	}
}
