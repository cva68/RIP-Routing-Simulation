from ripd.ripd import RIPDaemon
import sys
import logging

LOG_LEVEL = logging.DEBUG

if __name__ == "__main__":
    rip_daemon = RIPDaemon(sys.argv[1], log_level=LOG_LEVEL)
    rip_daemon.start()
