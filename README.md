# Palworld dedicated server helper
Helper utilities for managing a Palworld dedicated server in python. Send rcon commands, backup server, etc.

* underlying rcon implementation should work fine on any OS if you want to use it directly.
* `PalworldUtil` utilizes `steamcmd` and was only tested on Windows. Would likely work on linux with minor changes but is not currently implemented.

## Setup
* Install python: https://www.python.org/downloads/
* Install requirements: `pip install -r requirements.txt`

## Usage
* See `./src/example.py` for basic usage.
* See `./src/utility/palworld_util.py` for advanced params, etc.
* See `./src/server_watcher.py` for automatic server restarts, backups, etc.

# Contributing
Feel free to open issues or pull requests as long as they're constructive / useful.
