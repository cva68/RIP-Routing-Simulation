# Kahu's code here


import time
from ._structures import RIPEntry, RIPPacket


class RouteEntry:
    """
        Represents a single entry in the routing table.
        Stores the destination address, next hop, metric, and timeout.
    """
    def __init__(self, destination_id: int, next_hop_id: int,
                 metric: int, timeout: int):
        self.destination_id = destination_id
        self.next_hop_id = next_hop_id
        self.metric = metric
        self.timeout = timeout
        self.garbage_colletion = False

    def as_packet(self):
        """
            Convert the RouteEntry to a RipEntry for packet transmission.
        """
        return RIPEntry(
            id=self.destination_id,
            metric=self.metric
        )


class RouteTable:
    """
        Represents the full routing table.
        Contains a list of RouteEntry objects.
        Handles adding, removing, and retrieving routes.
    """
    def __init__(self, logger,
                 router_id: int, timeout: int = 30,
                 garbage_collection_time: int = 120):
        self._timeout = timeout
        self._garbage_collection_time = garbage_collection_time + timeout
        self._router_id = router_id
        self.routes = {}  # Dict of RouteEntry instances

        self._logger = logger
        self._logger.debug("Routing table initialized.")

    def __str__(self):
        """
            String representation of the routing table.
            Displays all routes in the table.
        """
        return "\n".join([f"Destination: {entry.destination_id}, "
                          f"Next Hop: {entry.next_hop_id}, "
                          f"Metric: {entry.metric}, "
                          f"Timeout: {entry.timeout}"
                          for entry in self.routes.values()])

    def add_route(self, destination_id, next_hop_id, metric, timeout=None):
        """
            Add a new route to the routing table.
            If the route already exists,
            update it with the new metric and timeout.
        """
        if timeout is None:
            timeout = time.time() + 180  # Need to do something abt this
        entry = RouteEntry(destination_id, next_hop_id, metric, timeout)
        self.routes[destination_id] = entry

    def remove_route(self, destination_id):
        """
            Remove a route from the routing table.
            If the route does not exist, do nothing.

            :return: True on successful removal, False otherwise.
        """
        # Find the entry with the matching destination and remove it
        try:
            self.routes.pop(destination_id)
            return True
        except KeyError:
            self._logger.warning(f"Requested deletion of {destination_id}," +
                                 " but route does not exist.")
            return False

    def remove_all(self):
        """
            Remove all routes from the routing table.
        """
        # Clear the list of routes
        self.routes.clear()

    def get_entry(self, destination_id):
        """
            Retrieve a route entry by destination address.
            Returns the RouteEntry object if found, otherwise None.
        """
        try:
            return self.routes[destination_id]
        except KeyError:
            self._logger.warning(f"Requested entry for {destination_id}," +
                                 " but route does not exist.")
            return

    def get_packet(self, destination_router_id):
        """
            Convert the routing table to a RipPacket for transmission.
            Returns a RipPacket object containing all routes.
        """
        # Cache the original metric for the destination router, then implement
        # poison reverse
        try:
            original_metric = self.routes[destination_router_id].metric
            self.routes[destination_router_id].metric = 16
        except KeyError:
            original_metric = None
            pass

        # Formulate the packet
        rip_entries = [entry.as_packet() for entry in self.routes.values()]

        # Restore the original metric for our own table
        if original_metric is not None:
            self.routes[destination_router_id].metric = original_metric

        # Create and return the packet
        return RIPPacket.construct(command=2, router_id=self._router_id,
                                   entries=rip_entries)

    def check_for_timeouts(self):
        """
            Check for timed out entries in the routing table.
            Remove any entries that have timed out.
        """
        # Check each entry for timeouts
        for router_id, entry in self.routes.items():
            # If the entry has timed out, start garbage collection timer
            # and set metric to 16
            if time.time() - entry.timeout > self._timeout:
                self._logger.debug(f"Entry for router {router_id} timed out.")
                entry.garbage_colletion = True
                entry.metric = 16

            # If the entry has been in garbage collection for too long,
            # remove it from the table
            elif time.time() - entry.timeout > self._garbage_collection_time:
                self._logger.debug(f"Garbage collection for router {router_id}\
                                    expired, deleting entry.")
                self.remove_route(router_id)
