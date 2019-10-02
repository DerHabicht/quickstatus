# Quick Status
A CLI utility for quickly setting Slack statuses.

## Dependencies

### Virtual Env
Create a new virtual environment based on the requirements.txt file in the repo.

### The Hard Way
If you do not have/are not willing to set up a virtual env, you will need to have
Python 3.6 and the following packages:

- docopt 0.6.2
- python-dotenv 0.10.1
- requests 2.21.0

## Setup
Before you start using this utility, you will have to create a new Slack app.
You can do this [here](https://api.slack.com/slack-apps). Once it has been
created, go to Permissions on the Basic Information page (or OAuth &
Permissions in the sidebar). Under scopes, add `users.profile:write` (Modify
user's profile). Once you save the changes, the button "Install App to
Workspace" at the top of the page will be enabled. Click it, authorize it, and
then copy the OAuth Access Token.

Create a .env file in the directory and add the line:

```
QS_TOKEN=[Your OAuth Access Token]
```

You will also need to create a `~/.quickstatus` directory. In this directory, copy over
the `statuses.json` file and create a `defaults.json` file with `{}` as its contents.

At some point (if I feel like it) I'll add an install script.

## Usage
Start by sourcing the environment (if you set it up):
```
source venv/bin/quickstatus
```

Running `python status.py -h` will provide you with details on how to use the script.

## Configuring Custom Statuses
The statuses that you can invoke are defined in the statuses.json file. An
example file is included in this repo. The `status_expiration` field is
optional and the values here are in minutes (i.e. `"status_expiration": 60`
will cause that status to expire in one hour by default). If an expiration is
given on the command line (also in minutes) that value will take precedence.

If you have a specific time in mind and don't want to do math, you can also use
timestamps in the form of `YYYY-MM-DDTHH:MM`.
