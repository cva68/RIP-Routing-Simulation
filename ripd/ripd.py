#!/usr/bin/env python3

"""
    ripd.py
    Entrypoint for the RIP Daemon
"""

import logging
import traceback
import time
from ._configloader import ConfigLoader
from ._structures import RIPPacket
from ._interface import Interface
from ._table import RouteTable

LOG_LEVEL = logging.DEBUG


class RIPDaemon:
    def __init__(self, config_file: str, log_level: int = LOG_LEVEL):
        """
            Initialize the RIP Daemon.

            :param config_file: Path to the configuration file.
            :param log_level: Log level for the RIP Daemon.
        """
        # Start the logger and load the configuration file
        self._logger = self._setup_logger(log_level)
        self._logger.debug("Loading configuration file.")
        self._config_loader = ConfigLoader(self._logger, config_file)

        # Load router config
        router_info = self._config_loader.get_router_info()
        self._id = router_info['router_id']
        self._ports = router_info['incoming_ports']
        self._bind = router_info['bind']
        self._periodic_update_time = router_info['periodic_update_time']
        self._garbage_collection_time = router_info['garbage_collection_time']
        self._timeout = router_info['timeout']

        # Load peer config
        self._peer_info = self._config_loader.get_peer_info()

        # Initialise routing table
        self._table = RouteTable(self._logger, self._id,
                                 self._timeout, self._garbage_collection_time)

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
        self._interface = Interface(self._logger, self._ports, self._bind)

        # Add this router to the table, with metric 0
        self._table.add_route(destination_id=self._id,
                              next_hop_id=self._id,
                              metric=0)

        # Set up periodic update timer
        self._next_periodic_update = time.time()

        # Main loop
        try:
            self._logger.info('RIP Daemon started.')

            # Main loop
            while True:
                # Process incoming data
                self._process_incoming_data()

                # Send periodic updates
                if time.time() >= self._next_periodic_update:
                    self._periodic_update()
                    self._logger.info(f"Table contents\n{self._table}")

                # Check for timed out entries, and entries that require
                # garbage collection
                self._table.check_for_timeouts()

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
            parse_result = RIPPacket.parse(packet_data)

            # On error, log and continue
            if not parse_result:
                self._logger.error("Failed to parse incoming packet.")
                self._logger.debug("Packet data: %s", packet_data)
                continue

            # Unpack the packet
            _command, router_id, entries = parse_result
            self._logger.debug(f"Parsed packet: {_command}, {router_id}," +
                               "{entries}")

            # Add entries to the routing table
            for entry in entries:
                metric = entry.metric + self._peer_info[router_id]['metric']
                self._table.add_route(destination_id=entry.id,
                                      next_hop_id=router_id,
                                      metric=metric)
