"""Utility for server administration via source rcon."""
import socket
import struct

from dataclasses import dataclass

from loguru import logger


@dataclass
class RCONPacketType:
    SERVERDATA_AUTH: int = 3
    SERVERDATA_AUTH_RESPONSE: int = 2
    SERVERDATA_EXECCOMMAND: int = 2
    SERVERDATA_RESPONSE_VALUE: int = 0


@dataclass
class RconPacket:
    # https://developer.valvesoftware.com/wiki/Source_RCON_Protocol#Basic_Packet_Structure
    size: int = None
    id: int = None
    type: RCONPacketType = None
    body: str = None
    terminator: bytes = b"\x00"
    RCON_PACKET_HEADER_LENGTH = 12
    RCON_PACKET_TERMINATOR_LENGTH = 2

    def pack(self):
        body_encoded = (
            self.body.encode("ascii") + self.terminator
        )  # The packet body field is a null-terminated string encoded in ASCII
        self.size = (
            len(body_encoded) + 10
        )  # Only value that can change is the length of the body, so do len(body) + 10.
        return (
            struct.pack("<iii", self.size, self.id, self.type)
            + body_encoded
            + self.terminator
        )

    @staticmethod
    def unpack(packet: bytes):
        if len(packet) < RconPacket.RCON_PACKET_HEADER_LENGTH:
            return RconPacket(size=None, id=None, type=None, body="Invalid packet")

        size, request_id, type = struct.unpack(
            "<iii", packet[: RconPacket.RCON_PACKET_HEADER_LENGTH]
        )
        body = packet[
            RconPacket.RCON_PACKET_HEADER_LENGTH : -RconPacket.RCON_PACKET_TERMINATOR_LENGTH
        ].decode("utf-8", errors="replace")
        return RconPacket(size=size, id=request_id, type=type, body=body)


class SourceRcon:
    def __init__(self, server_ip: str, rcon_port: int, rcon_password: str) -> None:
        self.SERVER_IP = server_ip
        self.RCON_PORT = rcon_port
        self.RCON_PASSWORD = rcon_password

        self.AUTH_FAILED_RESPONSE = -1

    def create_packet(
        self,
        command: str,
        request_id: int = 1,
        type: RCONPacketType = RCONPacketType.SERVERDATA_EXECCOMMAND,
    ):
        packet = RconPacket(id=request_id, type=type, body=command)
        final_packet = packet.pack()

        logger.debug(f"Final packet: {final_packet}")
        return final_packet

    def receive_all(self, sock: socket.socket, bytes_in: int = 4096) -> bytes:
        response = b""
        while True:
            try:
                part = sock.recv(bytes_in)
                if not part:
                    break
                response += part
                if len(part) < bytes_in:
                    break
            except socket.error as e:
                logger.error(f"Error receiving data: {e}")
                break
        return response

    def check_auth_response(self, auth_response_packet: bytes) -> bool:
        unpacked_packet = RconPacket.unpack(auth_response_packet)

        if (
            unpacked_packet.size is None
            or unpacked_packet.type != RCONPacketType.SERVERDATA_AUTH_RESPONSE
        ):
            logger.error("Invalid response or wrong packet type.")
            return False

        return unpacked_packet.id != self.AUTH_FAILED_RESPONSE

    def auth_to_rcon(self, socket: socket.socket) -> bool:
        # Authenticate to server rcon before sending command
        logger.debug("Authenticating to server rcon before sending command.")
        auth_packet = self.create_packet(
            self.RCON_PASSWORD, type=RCONPacketType.SERVERDATA_AUTH
        )
        socket.sendall(auth_packet)

        # Get and parse authentication response
        auth_response = self.receive_all(socket)
        if self.check_auth_response(auth_response):
            logger.debug("rcon authentication successful.")
            return True
        else:
            logger.error("rcon authentication failed. Not running command.")
            return False

    def send_command(self, command: str) -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((self.SERVER_IP, self.RCON_PORT))
            except socket.error as e:
                connection_error_msg = (
                    f"Failed to connect to socket before sending command. Error: {e}"
                )
                logger.error(connection_error_msg)
                return connection_error_msg
            else:
                logger.debug("socket connection successful.")

            if self.auth_to_rcon(socket=s):
                # Send command
                command_packet = self.create_packet(command)
                s.sendall(command_packet)

                # Get command response
                response = self.receive_all(s)
                unpacked_packet = RconPacket.unpack(response)
                logger.debug(f"Command response: {unpacked_packet.body}")
                return unpacked_packet.body
