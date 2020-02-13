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
	"os"
)

// setCmd represents the set command
var setCmd = &cobra.Command{
	Use:   "set",
	Short: "Set a status in Slack.",
	Long:  `Set a status in Slack from the configured list of "canned" statuses.`,
	Args:  cobra.RangeArgs(1, 2),
	Run: func(cmd *cobra.Command, args []string) {
		status, ok := C.CannedStatuses[args[0]]
		if !ok {
			fmt.Printf("%s is not a valid status. Valid statuses are:\n", args[0])
			C.ListValidStatuses()
			os.Exit(1)
		}

		var expires int64
		if status.StatusExpiration != nil {
			expires = 0
		} else {
			expires = *status.StatusExpiration
		}

		if err := C.Agent.SetUserCustomStatus(
			status.StatusText,
			status.StatusEmoji,
			expires,
		); err != nil {

		}
	},
}

func init() {
	rootCmd.AddCommand(setCmd)
}
