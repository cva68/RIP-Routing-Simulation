"""
    RIPDaemon - scheduller and incoming packet handler.
    MIT License. Copyright © 2025 Connor Varney, Kahu Jones
"""

import logging
import traceback
import time
import os
from ._configloader import ConfigLoader
from ._structures import (RIPPacket, PacketVersionError, PacketCommandError,
                          PacketParseError)
from ._interface import Interface
from ._table import RouteTable

LOG_LEVEL = logging.DEBUG
TABLE_PRINT_PERIOD = 0.5  # Seconds


class RIPDaemon:
    def __init__(self, config_file: str, log_level: int = LOG_LEVEL):
        """
            Initialize the RIP Daemon.

            :param config_file: Path to the configuration file.
            :param log_level: Log level for the RIP Daemon.
        """
        # Start the logger and load the configuration file
        self._log_level = log_level
        self._logger = self._setup_logger(log_level)
        self._logger.debug("Loading configuration file.")
        self._config_loader = ConfigLoader(self._logger, config_file)

        # Load router config
        router_info = self._config_loader.get_router_info()
        self._id = router_info['router_id']
        self._ports = router_info['incoming_ports']
        self._periodic_update_time = router_info['periodic_update_time']
        self._garbage_collection_time = router_info['garbage_collection_time']
        self._timeout = router_info['timeout']

        # Load peer config
        self._peer_info = self._config_loader.get_peer_info()

        # Initialise routing table
        self._table = RouteTable(self._logger, self._id,
                                 self._timeout, self._garbage_collection_time)

        # Flag for integration tests to cleanly exit
        self._run = True

    def _setup_logger(self, log_level: int):
        """
            Setup logger for the RIP Daemon.

            :returns: Logger object.
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        return logger

    def start(self):
        """
            Start the RIP Daemon.
        """
        self._logger.info("Starting RIP Daemon.")

        # Initialise interface
        self._interface = Interface(self._logger, self._ports)

        # Set up periodic update timer and table print timer
        self._next_periodic_update = time.time()
        self._next_table_print = time.time()

        # Main loop
        try:
            self._logger.info('RIP Daemon started.')

            # Main loop
            while self._run:
                # Process incoming data
                self._process_incoming_data()

                # Send periodic updates
                if time.time() >= self._next_periodic_update:
                    self._periodic_update()

                # Periodically print table
                if time.time() >= self._next_table_print:
                    if self._log_level == logging.INFO:
                        os.system('clear')
                    self._logger.info(f"Routing Table for Router {self._id}:" +
                                      f"\n{self._table}")
                    self._next_table_print = time.time() + TABLE_PRINT_PERIOD

                # Check for timed out entries, and entries that require
                # garbage collection
                timed_out = self._table.check_for_timeouts()

                # If any entries have timed out, send a triggered update
                if timed_out:
                    self._logger.debug("Timed out entry/entries detected, " +
                                       "sending triggered update.")
                    self._periodic_update()

        except KeyboardInterrupt:
            self._logger.info("Exiting RIP Daemon.")

        except Exception:
            self._logger.error("An error occurred:\n%s",
                               traceback.format_exc())

        finally:
            self._logger.debug("Closing sockets.")
            self._interface.close_sockets()

    def _periodic_update(self):
        """
            Send periodic updates to all peers.
        """
        self._logger.debug("Sending periodic update.")

        # Send periodic updates to all peers
        for router_id, info in self._peer_info.items():
            packet = self._table.get_packet(router_id)
            self._interface.unicast(packet, info['port'])

        # Reset periodic update time
        self._next_periodic_update = time.time() + self._periodic_update_time

    def _process_incoming_data(self):
        """
            Process incoming data from the interface, adding entries to the
            routing table if required.
        """
        incoming_data = self._interface.poll_incoming_ports()

        # If no data, return
        if not incoming_data:
            return

        self._logger.debug("Incoming packet received.")
        # Process incoming packets
        for packet in incoming_data:
            packet_data = packet[0]

            # Attempt to parse the packet
            try:
                parse_result = RIPPacket.parse(packet_data)
            except (PacketVersionError, PacketCommandError, PacketParseError) \
                    as e:
                self._logger.error(f"Failed to parse incoming packet: {e}.")
                self._logger.debug("Packet data: %s", packet_data)
                continue  # Drop the packet and continue

            # Unpack the packet
            _command, source_router_id, entries = parse_result
            self._logger.debug(f"Parsed packet: {parse_result}")

            # Add entries to the routing table
            for entry in entries:
                # Ignore the entry if it is for this router
                if entry.id == self._id:
                    continue

                # Calculate the metric of this entry
                new_metric = min(entry.metric +
                                 self._peer_info[source_router_id]['metric'],
                                 16)

                if entry.id not in self._table.routes.keys():
                    if new_metric < 16:
                        # New route, not in table yet and it's valid
                        self._table.add_route(destination_id=entry.id,
                                              next_hop_id=source_router_id,
                                              metric=new_metric)

                elif (self._table.routes[entry.id].next_hop_id ==
                      source_router_id):
                    # This is an update from the same next hop — must always
                    # accept changes

                    if new_metric >= 16:
                        # If the metric is already 16, and this is another
                        # metric 16, ignore this as to not restart garbage
                        # collection timer
                        if self._table.routes[entry.id].metric == 16:
                            continue

                        # Otherwise, set the timeout of the entry to now, to
                        # trigger the garbage collection timer
                        timeout = time.time() - self._timeout
                        self._table.routes[entry.id].timeout = timeout

                    else:
                        # If this route doesn't have metric 16, use normal
                        # timeout val
                        self._table.routes[entry.id].timeout = time.time()

                    self._table.routes[entry.id].metric = new_metric

                elif new_metric < self._table.routes[entry.id].metric:
                    # Better route (lower metric) from a different next hop
                    self._table.add_route(destination_id=entry.id,
                                          next_hop_id=source_router_id,
                                          metric=new_metric)
