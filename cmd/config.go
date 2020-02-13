package cmd

import (
	"fmt"
	"os"

	"github.com/mitchellh/go-homedir"
	"github.com/spf13/viper"

	"github.com/derhabicht/quickstatus/context"
)

// Default canned status list for generating a new context.
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

func setViperDefaults() {
	viper.SetDefault(context.SlackAPIToken, "")
	viper.SetDefault(context.CannedStatuses, defaultCannedStatuses)
	viper.SetDefault(context.DefaultStatuses, "[]")
}

var C context.Context

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
		fmt.Println("Failed to read context file")
		if err := viper.WriteConfigAs(fmt.Sprintf("%s/.quickstatus.yaml", home)); err != nil {
			fmt.Printf("Could not write context file: %s", err)
		}
	}

	viper.AutomaticEnv()

	if err := C.New(); err != nil {
		panic(err)
	}
}
