#!/usr/bin/env python3

"""
    ripd.py
    Entrypoint for the RIP Daemon
"""

import logging
from _configloader import ConfigLoader

LOG_LEVEL = logging.INFO


class RIPDaemon:
    def __init__(self, config_file: str, log_level: int = LOG_LEVEL):
        """
            Initialize the RIP Daemon.

            :param config_file: Path to the configuration file.
            :param log_level: Log level for the RIP Daemon.
        """
        self._config_loader = ConfigLoader(config_file)
        self._logger = self._setup_logger(log_level)

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
        router_info = self._config_loader.get_router_info()
        peer_info = self._config_loader.get_peer_info()

        # Test the configuration loader
        self._logger.info(f"Router ID: {router_info['router_id']}")
        self._logger.info(f"Incoming Ports: {router_info['incoming_ports']}")
        self._logger.info(f"Peer Information: {peer_info}")


if __name__ == "__main__":
    rip_daemon = RIPDaemon('config/sample.ini')
    rip_daemon.start()
