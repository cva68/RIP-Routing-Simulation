# Kahu's code here


import time
from _structures import RipEntry, RipPacket




class RouteEntry:
    """
        Represents a single entry in the routing table.
        Stores the destination address, next hop, metric, and timeout.
    """
    def __init__(self, destination, next_hop, metric, timeout, garbage_collect=None):
        self.destination = destination
        self.next_hop = next_hop
        self.metric = metric
        self.timeout = timeout
        self.garbage_collect = garbage_collect

    def as_packet(self):
        """
            Convert the RouteEntry to a RipEntry for packet transmission.
        """
        
        return RipEntry(
            addr=self.destination,
            next_hop=self.next_hop, # Needs to be added to RipEntry - Assumed it would be neeeded. 
            metric=self.metric
        )

class RouteTable:
    """
        Represents the full routing table.
        Contains a list of RouteEntry objects.
        Handles adding, removing, and retrieving routes.
    """
    def __init__(self):
        self.routes = []  # List of RouteEntry  - Container for all routes

    def add_route(self, destination, next_hop, metric):
        """
            Add a new route to the routing table.
            If the route already exists, update it with the new metric and timeout.
        """
        timeout = time.time() + 180  
        entry = RouteEntry(destination, next_hop, metric, timeout)
        self.routes.append(entry)

    def remove_route(self, destination):
        """
            Remove a route from the routing table.
            If the route does not exist, do nothing.
        """
        # Find the entry with the matching destination and remove it
        self.routes = [entry for entry in self.routes if entry.destination != destination]

    def remove_all(self):
        """
            Remove all routes from the routing table.
        """
        # Clear the list of routes
        self.routes.clear()

    def get_entry(self, destination):
        """
            Retrieve a route entry by destination address.
            Returns the RouteEntry object if found, otherwise None.
        """
        for entry in self.routes:
            if entry.destination == destination:
                return entry
        return None

    def get_packet(self):
        """
            Convert the routing table to a RipPacket for transmission.
            Returns a RipPacket object containing all routes.
        """
        rip_entries = [entry.as_packet() for entry in self.routes]
        return RipPacket(rip_entries)
