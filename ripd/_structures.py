#!/usr/bin/env python3
"""
    _structures.py
    Handlers for RIP packet structures and RIP entry structures.
"""

from ._helpers import IPTools
from ._exceptions import PacketParseError

HEADER_LENGTH = 4
ENTRY_LENGTH = 20
ADDRESS_FAMILY = 2
VERSION = 2


class PacketCommands:
    REQUEST = 1
    RESPONSE = 2


class RIPPacket:
    """
        Static helper functions for constructing and parsing RIP packets.
    """

    @staticmethod
    def construct(command: int, entries: list = [], version: int = VERSION):
        """
            Construct a RIP packet.

            :param command: The command field of the RIP packet (e.g., request
                            or response).
            :param entries: A list of RIPEntry elements to include in the
                            packet.
            :param version: The RIP version number (default is VERSION).
            :returns: Bytearray of the constructed RIP packet.
        """
        # Calculate the length of the packet and initialize the bytearray
        packet_length = HEADER_LENGTH + len(entries) * ENTRY_LENGTH
        packet = bytearray(packet_length)

        # Construct the header
        packet[0] = command
        packet[1] = version
        packet[2] = 0
        packet[3] = 0

        # Construct the entries
        for i, entry in enumerate(entries):
            packet[4 + i * ENTRY_LENGTH: 4 + (i + 1) * ENTRY_LENGTH] = \
                entry.as_packet()

        return packet

    @staticmethod
    def parse(packet):
        """
            Deconstruct a RIP packet.

            :returns: The command (PacketCommand), and a list of
            RIPEntry objects.
            :raises: PacketParseError if the packet is invalid.
        """
        # Parse the header
        command = packet[0]
        version = packet[1]

        # Verify the version matches the version of this implementation
        if version != VERSION:
            raise PacketParseError("Invalid RIP version in packet")

        # Verify we've received a valid command
        if command not in [PacketCommands.REQUEST, PacketCommands.RESPONSE]:
            raise PacketParseError("Invalid RIP command in packet")

        # If the command is a request, return an empty list. The
        # response to this request will be handled upstream.
        if command == PacketCommands.REQUEST:
            return PacketCommands.REQUEST, []

        # Parse the entries
        entries = []
        for i in range(4, len(packet), ENTRY_LENGTH):
            try:
                ip = IPTools.bytes_to_ip(packet[i + 4:i + 8])
                metric = int.from_bytes(packet[i + 16:i + 20], 'big')
            except IndexError:
                raise PacketParseError("Invalid packet length")
            entries.append(RIPEntry(ip, metric))

        return PacketCommands.RESPONSE, entries


class RIPEntry:
    """
        Basic structure for a RIP entry.
    """
    def __init__(self, address, metric, afi=ADDRESS_FAMILY):
        """
            Initialize a RIP entry.
        """
        self.address = address
        self.metric = metric
        self.afi = afi

    def as_packet(self):
        """
                Convert the RIP entry to a bytearray.
        """
        # Convert the IP address to a bytearray
        ip_bytes = IPTools.ip_to_bytes(self.address)

        # Create the packet
        packet = bytearray(ENTRY_LENGTH)
        packet[0:2] = self.afi.to_bytes(2, 'big')
        packet[2] = 0
        packet[3] = 0
        packet[4:8] = ip_bytes
        packet[8:16] = bytes([0] * 8)
        packet[16:20] = self.metric.to_bytes(4, 'big')

        print(len(packet))
        return packet
