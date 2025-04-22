import unittest
import time
from unittest.mock import patch
from test.context import (
    RouteEntry,
    RouteTable,
    RIPEntry,
)


class TestRouteEntry(unittest.TestCase):

    def test_as_packet(self):
        entry = RouteEntry("192.168.1.0", "192.168.1.1", 1, time.time())
        packet = entry.as_packet()

        self.assertIsInstance(packet, RIPEntry)
        self.assertEqual(packet.addr, "192.168.1.0")
        self.assertEqual(packet.next_hop, "192.168.1.1")
        self.assertEqual(packet.metric, 1)


class TestRouteTable(unittest.TestCase):

    def setUp(self):
        self.table = RouteTable()

    def test_add_and_get_route(self):
        self.table.add_route("10.0.0.0", "10.0.0.1", 2)
        entry = self.table.get_entry("10.0.0.0")

        self.assertIsNotNone(entry)
        self.assertEqual(entry.destination, "10.0.0.0")
        self.assertEqual(entry.next_hop, "10.0.0.1")
        self.assertEqual(entry.metric, 2)

    def test_remove_route(self):
        self.table.add_route("10.0.0.0", "10.0.0.1", 2)
        self.table.remove_route("10.0.0.0")
        self.assertIsNone(self.table.get_entry("10.0.0.0"))

    def test_remove_all_routes(self):
        self.table.add_route("10.0.0.0", "10.0.0.1", 2)
        self.table.add_route("10.0.1.0", "10.0.1.1", 3)
        self.table.remove_all()
        self.assertEqual(len(self.table.routes), 0)

    @patch('context.RipPacket')
    def test_get_packet(self, mock_rip_packet):
        
        entry1 = RouteEntry("10.0.0.0", "10.0.0.1", 1, time.time())
        entry2 = RouteEntry("10.0.1.0", "10.0.1.1", 2, time.time())

        self.table.routes = [entry1, entry2]

        self.table.get_packet()

        expected = [entry1.as_packet(), entry2.as_packet()]
        mock_rip_packet.assert_called_once_with(expected)


if __name__ == "__main__":
    unittest.main()
