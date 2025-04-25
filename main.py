"""
    RIPDaemon entry point.
    MIT License. Copyright © 2025 Connor Varney, Kahu Jones
"""

from ripd.ripd import RIPDaemon
import sys
import logging

LOG_LEVEL = logging.INFO

if __name__ == "__main__":
    # Set log level to debug if verbose flag passed
    if len(sys.argv) > 2:
        if sys.argv[2] == "--verbose" or sys.argv[2] == "-v":
            LOG_LEVEL = logging.DEBUG

    # Begin the RIPDaemon
    rip_daemon = RIPDaemon(sys.argv[1], log_level=LOG_LEVEL)
    rip_daemon.start()
