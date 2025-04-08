#!/usr/bin/env python3

"""
    ripd.py
    Entrypoint for the RIP Daemon
"""

import logging
import traceback
from socket import socket, AF_INET, SOCK_DGRAM, error
from ripd._configloader import ConfigLoader

LOG_LEVEL = logging.DEBUG


class RIPDaemon:
    def __init__(self, config_file: str, log_level: int = LOG_LEVEL):
        """
            Initialize the RIP Daemon.

            :param config_file: Path to the configuration file.
            :param log_level: Log level for the RIP Daemon.
        """
        self._config_loader = ConfigLoader(config_file)
        self._logger = self._setup_logger(log_level)
        self._sockets = []

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

    def _bind_sockets(self):
        """
            Try bind to each input port from the configuration file
        """
        for port in self._ports:
            try:
                self._logger.debug("Binding to port %d", port)
                self._sockets.append(socket(AF_INET, SOCK_DGRAM))
                self._sockets[-1].setblocking(1)
                self._sockets[-1].settimeout(1)
            except error:
                self._logger.critical("Socket creation failed")
                self.exit(1)

            try:
                self._logger.debug("Binding to %s:%d", self._bind, port)
                self._sockets[-1].bind((self._bind, port))
            except error:
                self._logger.critical("Socket binding failed")
                self.exit(1)

    def _close_sockets(self):
        """
            Close all sockets
        """
        self._logger.debug("Closing sockets")
        for sock in self._sockets:
            sock.close()

    def start(self):
        """
            Start the RIP Daemon.
        """
        self._logger.info("Starting RIP Daemon.")
        self._logger.debug("Loading configuration file.")
        # Load router config
        router_info = self._config_loader.get_router_info()
        self._id = router_info['router_id']
        self._ports = router_info['incoming_ports']
        self._bind = router_info['bind']

        # Load peer config
        self._peer_info = self._config_loader.get_peer_info()

        # Bind sockets
        self._bind_sockets()

        # Main loop
        try:
            self._logger.info('RIP Daemon started.')
            while True:
                # Do things here
                pass

        except KeyboardInterrupt:
            self._logger.info("Exiting RIP Daemon.")

        except Exception:
            self._logger.error("An error occurred:\n%s",
                               traceback.format_exc())

        finally:
            self._close_sockets()


if __name__ == "__main__":
    rip_daemon = RIPDaemon('config/sample.ini')
    rip_daemon.start()
