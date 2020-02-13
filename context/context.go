package context

import (
	"encoding/json"
	"fmt"
	"github.com/pkg/errors"
	"github.com/spf13/viper"
	"sort"

	"github.com/derhabicht/quickstatus/agent"
)

// SlackAPIToken is the key for looking up the Slack API user token from the context. This has to be manually set by
// the user after a context has been automatically generated.
const SlackAPIToken = "slack_api_token"

// CannedStatuses is the key for looking up the canned statuses map in the context. The configuration value is in JSON
// and is unmarshaled on start-up to the context.
const CannedStatuses = "canned_statuses"

// DefaultStatuses is the key for looking up the default statuses stack from the context. The configuration value is in
// JSON and is marshaled/unmarshaled to/from the context.
const DefaultStatuses = "default_statuses"

// Context contains unmarshaled configuration payloads and an agent for interacting with the Slack API.
type Context struct {
	Agent           agent.Agent
	CannedStatuses  map[string]agent.Status
	DefaultStatuses []agent.Status
}

// New creates a new context by parsing the relevant information out of the configuration.
func (c *Context) New() error {
	c.Agent = agent.New(viper.GetString(SlackAPIToken))

	c.CannedStatuses = make(map[string]agent.Status)
	if err := json.Unmarshal([]byte(viper.GetString(CannedStatuses)), &c.CannedStatuses); err != nil {
		return errors.WithMessage(err, "unable to parse canned statuses")
	}

	if err := json.Unmarshal([]byte(viper.GetString(DefaultStatuses)), &c.DefaultStatuses); err != nil {
		return errors.WithMessage(err, "unable to parse default statuses")
	}

	return nil
}

// WriteDefaultStatuses writes the default status stack into the context. This is called to ensure persistence across
// command executions.
func (c *Context) WriteDefaultStatuses() error {
	d, err := json.Marshal(c.DefaultStatuses)
	if err != nil {
		return errors.WithStack(err)
	}

	viper.Set(DefaultStatuses, string(d))
	if err := viper.WriteConfig(); err != nil {
		return errors.WithStack(err)
	}

	return nil
}

// ListValidStatuses prints a list of the canned statuses that are stored in the context.
func (c *Context) ListValidStatuses() {
	keys := make([]string, len(c.CannedStatuses))
	i := 0
	for k := range c.CannedStatuses {
		keys[i] = k
		i++
	}

	sort.Strings(keys)

	for _, v := range keys {
		fmt.Printf("  %s\n", v)
	}
}
