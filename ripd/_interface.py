import logging
from socket import socket, AF_INET, SOCK_DGRAM, error


class Interface:
    """
        Interface class for the ripd module.
        Used to bind ports and handle incoming packets.
    """

    def __init__(self, incoming_ports, bind):
        """
        Initialize the Interface class.
        """
        self._logger = logging.getLogger(__name__)
        self._sockets = []
        self._bind = bind
        self._ports = incoming_ports

        self._bind_sockets()

    def _bind_sockets(self):
        """
            Try bind to each input port from the configuration file, and
            to the bind address of this router.
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

    def broadcast(self, packet):
        """
            Broadcast a packet to all sockets.
        """
        for sock in self._sockets:
            try:
                # This probably isn't right, need UDP broadcast
                sock.sendto(packet, (self._bind, sock.getsockname()[1]))
            except error:
                self._logger.critical("Socket send failed")
                self.exit(1)
