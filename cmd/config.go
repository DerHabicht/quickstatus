package cmd

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/mitchellh/go-homedir"
	"github.com/pkg/errors"
	"github.com/spf13/viper"

	"github.com/derhabicht/quickstatus/slack"
)

const defaultCannedStatuses = `{
  "commute": {
    "status_text": "Commuting",
    "status_emoji": ":bus:",
    "status_expiration": 90,
    "disturb": true
  },
  "home": {
    "status_text": "Working remotely",
    "status_emoji": ":house_with_garden:",
    "disturb": true
  },
  "huddle": {
    "status_text": "Huddling",
    "status_emoji": ":dugtrio:",
    "disturb": false
  },
  "lunch": {
    "status_text": "Out to lunch",
    "status_emoji": ":poultry_leg:",
    "status_expiration": 60,
    "disturb": true
  },
  "meet": {
    "status_text": "In a meeting",
    "status_emoji": ":spiral_calendar_pad:",
    "status_expiration": 60,
    "disturb": false
  },
  "office": {
    "status_text": "In the office",
    "status_emoji": ":office:",
    "disturb": true
  },
  "pom": {
    "status_text": "Focusing",
    "status_emoji": ":tomato:",
    "status_expiration": 25,
    "disturb": false
  },
  "travel": {
    "status_text": "Travelling",
    "status_emoji": ":airplane:",
    "disturb": false
  }
}`

var C Context

type Context struct {
	CannedStatuses      map[string]slack.Status
	DefaultStatuses     []slack.Status
}

func NewContext() (Context, error) {
	c := Context{}

	c.CannedStatuses = make(map[string]slack.Status)
	if err := json.Unmarshal([]byte(viper.GetString("canned_statuses")), &c.CannedStatuses); err != nil {
		return c, errors.WithMessage(err, "unable to parse canned statuses")
	}

	if err := json.Unmarshal([]byte(viper.GetString("default_statuses")), &c.DefaultStatuses); err != nil {
		return c, errors.WithMessage(err, "unable to parse default statuses")
	}

	return c, nil
}

func setViperDefaults() {
	viper.SetDefault("slack_api_token", "")
	viper.SetDefault("dnd_default_timeout", 60)
	viper.SetDefault("canned_statuses", defaultCannedStatuses)
	viper.SetDefault("default_statuses", "[]")
}

func initConfig() {
	setViperDefaults()

	var home string
	if cfgFile != "" {
		viper.SetConfigFile(cfgFile)
	} else {
		var err error
		home, err = homedir.Dir()
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		viper.AddConfigPath(home)
		viper.SetConfigName(".quickstatus")
	}

	if err := viper.ReadInConfig(); err != nil {
		fmt.Println("Failed to read config file")
		if err := viper.WriteConfigAs(fmt.Sprintf("%s/.quickstatus.yaml", home)); err != nil {
			fmt.Printf("Could not write config file: %s", err)
		}
	}

	viper.AutomaticEnv()

	var err error
	C, err = NewContext()
	if err != nil {
		panic(err)
	}
}

