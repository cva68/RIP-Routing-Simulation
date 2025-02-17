#!/usr/bin/env python3
"""
    _configloader.py
    Configuration loader for the RIP Daemon. See config/sample.ini for an
    example configuration file.
"""

import configparser
import logging
import sys


class ConfigLoader:
    """
        Class to load router information and peer information from a
        configuration file.
    """
    def __init__(self, config_file: str):
        self._config = configparser.ConfigParser()
        self._config.read(config_file)
        self._logger = logging.getLogger(__name__)

    def get_router_info(self):
        """
            Get router information from the configuration file.

            :returns: Dictionary containing router ID and list of incoming
                      ports.
        """
        try:
            router_info = {}
            router_info['router_id'] = self._config['ROUTER']['id']
            incoming_ports = self._config['ROUTER']['incoming_ports']
            router_info['incoming_ports'] = incoming_ports.split(', ')
            return router_info
        except (KeyError, ValueError):
            self._logger.critical("Invalid configuration file.")
            sys.exit(1)

    def get_peer_info(self):
        """
            Get peer information from the configuration file.

            :returns: List of dictionaries containing peer ports, metrics and
                      router IDs.
        """
        peer_info = []
        for section in self._config.sections():
            if 'PEER' in section:
                try:
                    peer = {}
                    peer['port'] = self._config[section]['port']
                    peer['metric'] = self._config[section]['metric']
                    peer['router_id'] = self._config[section]['router_id']
                    peer_info.append(peer)
                except (KeyError, ValueError):
                    self._logger.critical(f"Invalid configuration for peer \
                                          {section}.")
                    sys.exit(1)

        return peer_info
