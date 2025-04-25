#!/usr/bin/env python3
"""
    _configloader.py
    Configuration loader for the RIP Daemon. See config/sample.ini for an
    example configuration file.
"""

import configparser
import sys


class ConfigLoader:
    """
        Class to load router information and peer information from a
        configuration file.
    """
    def __init__(self, logger, config_file: str):
        self._config = configparser.ConfigParser()
        self._config.read(config_file)
        self._logger = logger

    def get_router_info(self):
        """
            Get router information from the configuration file.

            :returns: Dictionary containing router ID and list of incoming
                      ports.
        """
        try:
            router_info = {}
            router_info['router_id'] = int(self._config['ROUTER']['id'])
            incoming_ports = self._config['ROUTER']['incoming_ports']
            
            router_info['incoming_ports'] = incoming_ports.split(', ')
            for i, port in enumerate(router_info['incoming_ports']):
                router_info['incoming_ports'][i] = int(port)

            router_info['periodic_update_time'] = \
                int(self._config['ROUTER']['periodic_update_time'])
            router_info['garbage_collection_time'] = \
                int(self._config['ROUTER']['garbage_collection_time'])

            router_info['timeout'] = int(self._config['ROUTER']['timeout'])

            return router_info

        except (KeyError, ValueError):
            self._logger.critical("Invalid configuration file.")
            sys.exit(1)

    def get_peer_info(self):
        """
            Get peer information from the configuration file.

            :returns: Dictionary of peers, each peer being a dict containing
                        the port and metric.
        """
        peer_info = {}
        for section in self._config.sections():
            if 'PEER' in section:
                try:
                    peer = {}
                    peer['port'] = int(self._config[section]['port'])
                    peer['metric'] = int(self._config[section]['metric'])
                    peer_info[int(self._config[section]['router_id'])] = peer
                except (KeyError, ValueError):
                    self._logger.critical(f"Invalid configuration for peer \
                                          {section}.")
                    sys.exit(1)

        return peer_info
