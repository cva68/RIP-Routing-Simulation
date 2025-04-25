import unittest
import time
import logging
from test.context import (
    RouteEntry,
    RouteTable,
    RIPEntry,
    RIPPacket
)


class TestRouteEntry(unittest.TestCase):
    def test_as_packet(self):
        """
            Test the conversion of RouteEntry to RIPEntry packet.
        """
        entry = RouteEntry(destination_id=1, next_hop_id=2,
                           metric=1, timeout=time.time())
        packet = entry.as_packet()

        self.assertIsInstance(packet, RIPEntry)
        self.assertEqual(packet.id, 1)
        self.assertEqual(packet.metric, 1)


class TestRouteTable(unittest.TestCase):

    def setUp(self):
        """
            Initialise a routing table
        """
        logger = logging.getLogger(__name__)
        self.table = RouteTable(logger, router_id=0)

    def test_add_and_get_route(self):
        """
            Test adding a route and retrieving it.
        """
        self.table.add_route(destination_id=1, next_hop_id=2, metric=1)
        entry = self.table.get_entry(1)

        self.assertIsNotNone(entry)
        self.assertEqual(entry.destination_id, 1)
        self.assertEqual(entry.next_hop_id, 2)
        self.assertEqual(entry.metric, 1)

    def test_remove_route(self):
        """
            Test removing a route from the routing table.
            Ensure that the route is no longer present after removal.
        """
        self.table.add_route(destination_id=2, next_hop_id=1, metric=1)
        self.table.remove_route(1)
        self.assertIsNone(self.table.get_entry(1))

    def test_remove_all_routes(self):
        """
            Test removing all routes from the routing table.
        """
        self.table.add_route(destination_id=3, next_hop_id=2, metric=1)
        self.table.remove_all()
        self.assertEqual(len(self.table.routes), 0)

    def test_get_packet(self):
        """
            Test the conversion of the routing table to a RIP packet.
            Ensure that the packet contains the correct entries.
        """
        # Add entries to the table
        self.table.add_route(destination_id=1, next_hop_id=2, metric=1)
        self.table.add_route(destination_id=2, next_hop_id=3, metric=2)

        # Form the RIP packet
        packet = self.table.get_packet(destination_router_id=0)

        # Parse the packet, ensure we get the correct command and sender
        command, sender, entries = RIPPacket.parse(packet)
        self.assertEqual(command, 2)
        self.assertEqual(sender, 0)

        # Ensure number of entries is correct
        self.assertEqual(len(entries), 3)  # 2 + 1 for route to self

        # Ensure the first entry is a route to self w/ cost 0
        self.assertEqual(entries[0].id, 0)
        self.assertEqual(entries[0].metric, 0)

        # Ensure the second entry is a route to 1 w/ cost 1
        self.assertEqual(entries[1].id, 1)
        self.assertEqual(entries[1].metric, 1)

        # Ensure the first entry is a route to 2 w/ cost 2
        self.assertEqual(entries[2].id, 2)
        self.assertEqual(entries[2].metric, 2)

    def test_poison_reverse(self):
        """
            Ensure that we poison routes that have this router
            as the next hop
        """
        # Add entries to the table
        self.table.add_route(destination_id=5, next_hop_id=0, metric=1)

        # Form and parse the packet
        packet = self.table.get_packet(destination_router_id=0)
        command, sender, entries = RIPPacket.parse(packet)

        # Ensure the new entry has a metric of 16
        self.assertEqual(entries[-1].metric, 16)


if __name__ == "__main__":
    unittest.main()
