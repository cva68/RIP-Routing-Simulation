#!/usr/bin/env python3
"""
    _structures.py
    Handlers for RIP packet structures and RIP entry structures.
"""

from _helpers import IPTools

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

            :returns: Bytearray of the RIP packet.
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
        """
        # Parse the header
        command = packet[0]
        version = packet[1]

        # Verify the version matches the version of this implementation
        if version != VERSION:
            raise ValueError("Invalid RIP version")

        # Verify we've received a valid command
        if command not in [PacketCommands.REQUEST, PacketCommands.RESPONSE]:
            raise ValueError("Invalid RIP command")

        # If the command is a request, return an empty list. The
        # response to this request will be handled upstream.
        if command == PacketCommands.REQUEST:
            return PacketCommands.REQUEST, []

        # Parse the entries
        entries = []
        for i in range(4, len(packet), ENTRY_LENGTH):
            print(len(packet))
            entry = RIPEntry(address=packet[i:i + ENTRY_LENGTH],
                             metric=packet[i + ENTRY_LENGTH - 1])
            entries.append(entry)

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
        ip = IPTools.ip_to_bytes(self.address)

        # Create the packet
        packet = bytearray(ENTRY_LENGTH)
        packet[0] = 0
        packet[1] = self.afi  # MSB first
        packet[2] = 0
        packet[3] = 0
        packet[4:8] = ip
        packet[8:19] = bytes([0] * 12)
        packet[19] = self.metric

        return packet


if __name__ == "__main__":
    # Test the RIPEntry class
    # Something is wrong, ran out of time to fix.
    entry = RIPEntry(address="10.192.122.1", metric=1)
    advertisement = RIPPacket.construct(PacketCommands.RESPONSE, [entry])
    command, entries = RIPPacket.parse(advertisement)
    print(command)
    print(entries[0].address)
    print(entries[0].metric)
    print(entries[0].afi)
