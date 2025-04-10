#!/usr/bin/env python3

"""
    ripd.py
    Entrypoint for the RIP Daemon
"""

import logging
import traceback
from ._configloader import ConfigLoader
from ._interface import Interface

LOG_LEVEL = logging.DEBUG


class RIPDaemon:
    def __init__(self, config_file: str, log_level: int = LOG_LEVEL):
        """
            Initialize the RIP Daemon.

            :param config_file: Path to the configuration file.
            :param log_level: Log level for the RIP Daemon.
        """
        self._logger.debug("Loading configuration file.")
        self._config_loader = ConfigLoader(config_file)
        self._logger = self._setup_logger(log_level)
        self._sockets = []

        # Load router config
        router_info = self._config_loader.get_router_info()
        self._id = router_info['router_id']
        self._ports = router_info['incoming_ports']
        self._bind = router_info['bind']

        # Load peer config
        self._peer_info = self._config_loader.get_peer_info()

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
        interface = Interface(self._ports, self._bind)

        # Main loop
        try:
            self._logger.info('RIP Daemon started.')
            while True:
                # Do things here
                # Likely a round-robin scheduller
                pass

        except KeyboardInterrupt:
            self._logger.info("Exiting RIP Daemon.")

        except Exception:
            self._logger.error("An error occurred:\n%s",
                               traceback.format_exc())

        finally:
            interface._close_sockets()


if __name__ == "__main__":
    rip_daemon = RIPDaemon('config/sample.ini')
    rip_daemon.start()
