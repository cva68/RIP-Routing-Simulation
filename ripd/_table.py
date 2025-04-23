import time
from tabulate import tabulate
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

    def add_route(self, destination_id, next_hop_id, metric, timeout=None):
        """
            Add a new route to the routing table. If the route already exists,
            update it if a new hop is offering a lower metric, or the same hop
            has changed metric.
        """
        if timeout is None:
            timeout = time.time() + self._timeout

        # Ignore routes to self. These will have been poisoned regardless.
        if destination_id == self._router_id and metric != 0:
            return

        entry = None

        # If the destination already exists,
        if destination_id in self.routes:
            # And the metric of this new entry is less than the existing one,
            if metric < self.routes[destination_id].metric:
                # Use the new entry
                entry = RouteEntry(destination_id, next_hop_id,
                                   metric, timeout)
                self._logger.debug(f"Updating route for {destination_id} ")

            # Or, if the metric is higher or the same,
            if metric >= self.routes[destination_id].metric:
                # and the next hop is the same
                if self.routes[destination_id].next_hop_id == next_hop_id:
                    # Use the new entry
                    entry = RouteEntry(destination_id, next_hop_id,
                                       metric, timeout)
                    self._logger.debug(f"Updating metric for {destination_id}")

        else:
            # If the destination does not exist, create a new entry
            entry = RouteEntry(destination_id, next_hop_id,
                               metric, timeout)
            self._logger.debug(f"Adding new route for {destination_id}")

        # If we've established we should add the entry, do so now
        if entry is not None:
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
            self._logger.warning(f"Requested deletion of {destination_id}," +
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
            self._logger.warning(f"Requested entry for {destination_id}," +
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
            if entry.metric == 16:
                continue

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
        """
        # Check each entry for timeouts
        to_remove = []
        for router_id, entry in self.routes.items():
            # If the entry has been in garbage collection for too long,
            # remove it from the table
            if time.time() - entry.timeout > self._garbage_collection_time:
                self._logger.debug("Garbage collection for router " +
                                   f"{router_id} expired, deleting entry.")
                to_remove.append(router_id)

            # If the entry has timed out, start garbage collection timer
            # and set metric to 16
            if time.time() - entry.timeout > self._timeout:
                self._logger.debug(f"Entry for router {router_id} timed out.")
                entry.garbage_colletion = True
                entry.metric = 16

        # Remove any entries that have reached garbage collection time
        for router_id in to_remove:
            self.remove_route(router_id)
