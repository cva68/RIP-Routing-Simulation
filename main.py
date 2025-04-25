from ripd.ripd import RIPDaemon
import sys
import logging

LOG_LEVEL = logging.INFO

if __name__ == "__main__":
    if sys.argv[2] == "--verbose" or sys.argv[2] == "-v":
        LOG_LEVEL = logging.DEBUG
    rip_daemon = RIPDaemon(sys.argv[1], log_level=LOG_LEVEL)
    rip_daemon.start()
