/*
Copyright © 2020 Robert Hawk <robert@the-hawk.us>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/
package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// defaultCmd represents the default command
var defaultCmd = &cobra.Command{
	Use:   "default",
	Short: "Set a default status.",
	Long: `Mark a status in the list of configured canned statuses as a "default". When 'status clear' is invoked,
the actual Slack status will be set to this default instead. Defaults live on a stack and are popped off either
manually (via status default pop) or automatically as the default status expires.`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("default called")
	},
}

func init() {
	rootCmd.AddCommand(defaultCmd)
}
