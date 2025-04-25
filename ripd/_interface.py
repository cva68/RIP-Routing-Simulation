from socket import socket, AF_INET, SOCK_DGRAM, error
import select
import sys

POLL_TIMEOUT = 500  # Timeout on recieving incoming packets


class Interface:
    """
        Interface class for the ripd module.
        Used to bind ports and handle incoming packets.
    """

    def __init__(self, logger,
                 incoming_ports: list,
                 outgoing_ports: list,
                 bind_address="127.0.0.1",
                 ):
        """
        Initialize the Interface class.
        """
        # Store paramaters
        self._bind = bind_address
        self._incoming_ports = incoming_ports
        self._outgoing_ports = outgoing_ports

        # Configure logging
        self._logger = logger

        # Create sockets
        self._incoming_sockets = []
        self._bind_incoming_sockets()

        # Create a socket for outgoing packets
        self._outgoing_socket = socket(AF_INET, SOCK_DGRAM)

    def _bind_incoming_sockets(self):
        """
            Try bind to each input port from the configuration file, and
            to the bind address of this router.
        """
        self._poller = select.poll()  # Create a polle
        for port in self._incoming_ports:
            # Create sockets
            try:
                self._logger.debug(f"Creating socket on port {port}")
                self._incoming_sockets.append(socket(AF_INET, SOCK_DGRAM))
                self._incoming_sockets[-1].setblocking(1)
                self._incoming_sockets[-1].settimeout(1)
                self._poller.register(
                    self._incoming_sockets[-1],
                    select.POLLIN
                    )
            except error:
                self._logger.critical("Socket creation failed")
                sys.exit(1)

            # These are servers - bind sockets to ports
            # try:
            self._logger.debug(f"Binding to {self._bind}:{port}")
            self._incoming_sockets[-1].bind((self._bind, port))
            # except error:
            #     self._logger.critical("Socket binding failed")
            #     sys.exit(1)

    def close_sockets(self):
        """
            Close all sockets
        """
        self._logger.debug("Closing sockets")
        try:
            for sock in self._incoming_sockets:
                sock.close()
            self._outgoing_socket.close()
        except error:
            self._logger.critical("Failed to close sockets.")
            sys.exit(1)

    def unicast(self, packet, port):
        """
            Transmit a packet to a single other interface.
        """
        try:
            # getsockname()[1] is the port
            self._outgoing_socket.sendto(packet, (self._bind, port))
        except error:
            self._logger.critical("Socket send failed")
            sys.exit(1)

    def multicast(self, packet):
        """
            Multicast a packet to all other interfaces.
        """
        for port in self._outgoing_ports:
            self.unicast(packet, port)

    def poll_incoming_ports(self):
        """
            Poll all incoming ports for available UDP packets
            To be called by scheduller

            :returns: List of tuples containing the socket and the data
        """
        incoming_events = self._poller.poll(POLL_TIMEOUT)
        recieved_packets = []

        for event_socket, event in incoming_events:
            # Stop if no events  we have received an event
            if not (event and select.POLLIN):
                continue

            # Check each of our registered sockets for a match
            for registered_socket in self._incoming_sockets:
                # If this isn't the socket we received data on, continue
                if event_socket != registered_socket.fileno():
                    continue

                # Otherwise, get data from the socket and return it
                self._logger.debug('Recieved packet on port' +
                                   f' {registered_socket.getsockname()[1]}')
                # likely need to change this 4096, and include the src port
                recieved_packets.append(registered_socket.recvfrom(512))

        return recieved_packets
