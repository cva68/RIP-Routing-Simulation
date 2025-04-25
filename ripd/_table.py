"""
    RIPDaemon routing table structure, with timeout / garbage
    collection handling.
    MIT License. Copyright © 2025 Connor Varney, Kahu Jones
"""

import time
from tabulate import tabulate
from ._structures import RIPEntry, RIPPacket


class RouteEntry:
    """
        Represents a single entry in the routing table.
        Stores the destination address, next hop, metric, and timeout.
    """
    def __init__(self, destination_id: int, next_hop_id: int,
                 metric: int, timeout: int,
                 garbage_collection_timer: bool = False):
        self.destination_id = destination_id
        self.next_hop_id = next_hop_id
        self.metric = metric
        self.timeout = timeout
        self.garbage_collection_timer = garbage_collection_timer

    def as_list(self):
        """
            Convert the RouteEntry to a list for display.
        """
        timeout = max(0, int(time.time() - self.timeout))

        return [self.destination_id, self.next_hop_id,
                self.metric, timeout]

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
        entries = []
        for entry in self.routes.values():
            entries.append(entry.as_list())

            # Based on the timeout time, calculate the garbage collection time
            garbage_timer = int(time.time() - entry.timeout - self._timeout)
            garbage_timer = max(0, garbage_timer)  # Ensure positive numbers
            entries[-1].append(garbage_timer)

        return tabulate(entries,
                        headers=["Destination", "Next Hop",
                                 "Metric", "Timeout", "Garbage"],
                        tablefmt="fancy_grid")

    def add_route(self, destination_id, next_hop_id, metric,
                  timeout=None, garbage_collection_timer=False):
        """
            Add a new route to the routing table.
        """
        timeout = time.time() if timeout is None else timeout
        entry = RouteEntry(destination_id, next_hop_id, metric,
                           timeout, garbage_collection_timer)
        self.routes[destination_id] = entry

    def remove_route(self, destination_id):
        """
            Remove a route from the routing table.
            If the route does not exist, do nothing.

            :returns: True on successful removal, False otherwise.
        """
        # Find the entry with the matching destination and remove it
        try:
            self.routes.pop(destination_id)
            return True
        except KeyError:
            self._logger.debug(f"Requested deletion of {destination_id}," +
                               " but route does not exist.")
            return False

    def remove_all(self):
        """
            Remove all routes from the routing table.
        """
        self.routes.clear()

    def get_entry(self, destination_id):
        """
            Retrieve a route entry by destination address.
            Returns the RouteEntry object if found, otherwise None.
        """
        try:
            return self.routes[destination_id]
        except KeyError:
            self._logger.debug(f"Requested entry for {destination_id}," +
                               " but route does not exist.")
            return

    def get_packet(self, destination_router_id):
        """
            Convert the routing table to a RipPacket for transmission.
            Returns a RipPacket object containing all routes.
        """
        # Always include a route to this router with metric 0
        entries_to_transmit = [RIPEntry(id=self._router_id, metric=0)]

        # Append remaining entries, poisoning the metric where appropriate
        for entry in self.routes.values():
            if entry.next_hop_id == destination_router_id:
                metric = 16
            else:
                metric = entry.metric

            entries_to_transmit.append(RIPEntry(id=entry.destination_id,
                                                metric=metric))

        # Create and return the packet
        return RIPPacket.construct(command=2, router_id=self._router_id,
                                   entries=entries_to_transmit)

    def check_for_timeouts(self):
        """
            Check for timed out entries in the routing table.
            Remove any entries that have timed out.

            :returns: True if entries have timed out, false otherwise
        """
        # Check each entry for timeouts
        to_remove = []
        timed_out = False
        for router_id, entry in self.routes.items():
            # If the entry has been in garbage collection for too long,
            # remove it from the table
            if time.time() - entry.timeout > self._garbage_collection_time:
                self._logger.debug("Garbage collection for router " +
                                   f"{router_id} expired, deleting entry.")
                to_remove.append(router_id)

            # If the entry has timed out, start garbage collection timer
            # and set metric to 16
            if time.time() - entry.timeout >= self._timeout:
                if entry.garbage_collection_timer:
                    # If the entry is already in garbage collection, ignore
                    continue

                self._logger.debug(f"Entry for router {router_id} timed out.")
                self.routes[router_id].metric = 16
                self.routes[router_id].garbage_collection_timer = True
                timed_out = True

        # Remove any entries that have reached garbage collection time
        for router_id in to_remove:
            self.remove_route(router_id)

        # Return true if a triggered update is required for timed out entries
        return timed_out
