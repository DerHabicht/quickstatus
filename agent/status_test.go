package agent_test

import (
	"encoding/json"
	"github.com/derhabicht/quickstatus/agent"
	"github.com/stretchr/testify/assert"
	"testing"
)

func TestParseStatusWithExpMin(t *testing.T) {
	const status = `{
	  "status_text": "Happy First Flight day!",
	  "status_emoji": ":small_airplane:",
	  "status_expiration": 86400,
	  "disturb": true
	}`

	s := agent.Status{}
	err := json.Unmarshal([]byte(status), &s)
	assert.Nil(t, err)

	assert.Equal(t, "Happy First Flight day!", s.StatusText)
	assert.Equal(t, ":small_airplane:", s.StatusEmoji)
	assert.Equal(t, 86400, *s.StatusExpiration)
	assert.Equal(t, true, s.Disturb)
	assert.Nil(t, s.StatusExpirationTime)
}

func TestParseStatusWithoutExp(t *testing.T) {
	const status = `{
	  "status_text": "Happy First Flight day!",
	  "status_emoji": ":small_airplane:",
	  "disturb": true
	}`

	s := agent.Status{}
	err := json.Unmarshal([]byte(status), &s)
	assert.Nil(t, err)

	assert.Equal(t, "Happy First Flight day!", s.StatusText)
	assert.Equal(t, ":small_airplane:", s.StatusEmoji)
	assert.Equal(t, true, s.Disturb)
	assert.Nil(t, s.StatusExpiration)
	assert.Nil(t, s.StatusExpirationTime)
}

func TestParseStatusList(t *testing.T) {
	const statusList = `[
	  {
	    "status_text": "Happy First Flight day!",
	    "status_emoji": ":small_airplane:",
	    "status_expiration": 86400,
	    "disturb": true
	  },
	  {
	    "status_text": "Squawk 7600",
	    "status_emoji": ":giraffe_face:",
	    "status_expiration": 480,
	    "disturb": false
	  }
	]`

	var sl []agent.Status
	err := json.Unmarshal([]byte(statusList), &sl)
	assert.Nil(t, err)

	assert.Equal(t, "Happy First Flight day!", sl[0].StatusText)
	assert.Equal(t, ":small_airplane:", sl[0].StatusEmoji)
	assert.Equal(t, 86400, *sl[0].StatusExpiration)
	assert.Equal(t, true, sl[0].Disturb)
	assert.Nil(t, sl[0].StatusExpirationTime)

	assert.Equal(t, "Squawk 7600", sl[1].StatusText)
	assert.Equal(t, ":giraffe_face:", sl[1].StatusEmoji)
	assert.Equal(t, 480, *sl[1].StatusExpiration)
	assert.Equal(t, false, sl[1].Disturb)
	assert.Nil(t, sl[1].StatusExpirationTime)
}

func TestStatusParseMap(t *testing.T) {
	const statusList = `{
	  "wb": {
	    "status_text": "Happy First Flight day!",
	    "status_emoji": ":small_airplane:",
	    "status_expiration": 86400,
	    "disturb": true
	  },
	  "7600": {
	    "status_text": "Squawk 7600",
	    "status_emoji": ":giraffe_face:",
	    "status_expiration": 480,
	    "disturb": false
	  }
	}`

	sm := make(map[string]agent.Status)
	err := json.Unmarshal([]byte(statusList), &sm)
	assert.Nil(t, err)

	assert.Equal(t, "Happy First Flight day!", sm["wb"].StatusText)
	assert.Equal(t, ":small_airplane:", sm["wb"].StatusEmoji)
	assert.Equal(t, 86400, *sm["wb"].StatusExpiration)
	assert.Equal(t, true, sm["wb"].Disturb)
	assert.Nil(t, sm["wb"].StatusExpirationTime)

	assert.Equal(t, "Squawk 7600", sm["7600"].StatusText)
	assert.Equal(t, ":giraffe_face:", sm["7600"].StatusEmoji)
	assert.Equal(t, 480, *sm["7600"].StatusExpiration)
	assert.Equal(t, false, sm["7600"].Disturb)
	assert.Nil(t, sm["7600"].StatusExpirationTime)
}
