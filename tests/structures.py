"""
    Unit tests for the structures module.
    Author: C. Varney, K. Jones
"""

import unittest

from context import PacketCommands, RIPPacket, RIPEntry

HEADER_LENGTH = 4
ENTRY_LENGTH = 20
ADDRESS_FAMILY = 2
VERSION = 2


class RipEntryTestSuite(unittest.TestCase):
    """
        RIP Entry test suite.
    """
    def test_initialisation(self):
        """
            Test the initialisation of a RIP entry.
        """
        entry = RIPEntry(address="10.192.122.1", metric=1)
        self.assertEqual(entry.address, "10.192.122.1")
        self.assertEqual(entry.metric, 1)
    
    def test_packet_formation(self):
        """
            Test the formation of a RIP *entry* packet.
        """
        entry = RIPEntry(address="10.192.122.1", metric=1)
        packet = entry.as_packet()
        self.assertEqual(len(packet), 20)  # 20 bytes
        self.assertEqual(packet[0], 0)     # LSB should be 0
        self.assertEqual(packet[1], ADDRESS_FAMILY)  # AFI should be 2
        self.assertEqual(packet[2], 0)     # Reserved
        self.assertEqual(packet[3], 0)     # Reserved
        self.assertEqual(packet[4:8], bytes([10, 192, 122, 1]))  # IP address
        self.assertEqual(packet[8:16], bytes([0] * 8))  # Reserved
        self.assertEqual(
            packet[16:20],
            (1).to_bytes(4, byteorder='big')
        )  # Metric should be 1, big endian


class RipPacketTestSuite(unittest.TestCase):
    """
        RIP Packet test suite.
    """
    def test_initialisation(self):
        """
            Test the initialisation of a RIP packet.
        """
        packet = RIPPacket(command=PacketCommands.REQUEST)
        self.assertEqual(packet.command, PacketCommands.REQUEST)
        self.assertEqual(packet.entries, [])

    def test_packet_formation(self):
        pass


if __name__ == '__main__':
    unittest.main()
