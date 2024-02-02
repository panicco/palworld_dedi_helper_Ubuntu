# Created by PanicKode
# Simple RCON tool to send commands to a PalServer
from utility.palworld_util import PalworldUtil

import os
import sys

from loguru import logger


STEAMCMD_DIR = "/usr/games/"    # path to steamcmd install
SERVER_NAME = "EXAMPLE" # Server name
SERVER_IP = "1.1.1.1"   # Server IP address
RCON_PASSWORD = "password"  # Server Rcon Password
SERVER_PATH = "/home/<USER>/Steam/steamapps/common/PalServer/" # path to server files
RCON_PORT = 25575   # Port For RCON connection

# Change level to DEBUG if you want more logging.
logger.remove()
logger.add(sys.stderr, level="INFO")

# Create PalworldUtil instance with required vars only.
pal = PalworldUtil(STEAMCMD_DIR, SERVER_NAME, SERVER_IP, RCON_PORT, RCON_PASSWORD, SERVER_PATH)

def cmd_loop():
	while True:
		INCMD = input("Enter a Command to send:\n")
		response = pal.rcon.send_command(f"{INCMD}", [])
		logger.info(f"Commmand Response: {response}")


try:
	cmd_loop()
except KeyboardInterrupt:
        logger.info("Caught keyboard interrupt, ending...")
        sys.exit(0)
	
