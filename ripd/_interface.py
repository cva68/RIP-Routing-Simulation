import logging
from socket import socket, AF_INET, SOCK_DGRAM, error
import select
import sys
import time  # temporary


class Interface:
    """
        Interface class for the ripd module.
        Used to bind ports and handle incoming packets.
    """

    def __init__(self,
                 incoming_ports: list,
                 outgoing_ports: list,
                 bind_address: str,
                 poll_rate=5000
                 ):
        """
        Initialize the Interface class.
        """
        # Store paramaters
        self._bind = bind_address
        self._incoming_ports = incoming_ports
        self._outgoing_ports = outgoing_ports

        # Configure logging
        self._logger = logging.getLogger(__name__)

        # Create sockets
        self._incoming_sockets = []
        self._bind_incoming_sockets(poll_rate)

        # Create a socket for outgoing packets
        self._socket = socket(AF_INET, SOCK_DGRAM)

    def _bind_incoming_sockets(self, poll_rate):
        """
            Try bind to each input port from the configuration file, and
            to the bind address of this router.
        """
        poller = select.poll()  # Create a polle
        for port in self._incoming_ports:
            # Create sockets
            try:
                self._logger.debug(f"Creating socket on {port}")
                self._incoming_sockets.append(socket(AF_INET, SOCK_DGRAM))
                self._incoming_sockets[-1].setblocking(1)
                self._incoming_sockets[-1].settimeout(1)
                poller.register(self._incoming_sockets[-1], select.POLLIN)
            except error:
                self._logger.critical("Socket creation failed")
                sys.exit(1)

            # These are servers - bind sockets to ports
            try:
                self._logger.debug(f"Binding to {self._bind}:{port}")
                self._incoming_sockets[-1].bind((self._bind, port))
            except error:
                self._logger.critical("Socket binding failed")
                sys.exit(1)
        
        # Start the poller
        self._incoming_events = poller.poll(poll_rate)

    def close_sockets(self):
        """
            Close all sockets
        """
        self._logger.debug("Closing sockets")
        try:
            for sock in self._incoming_sockets:
                sock.close()
            self._socket.close()
        except error:
            self._logger.critical("Failed to close sockets.")
            sys.exit(1)

    def broadcast(self, packet):
        """
            'Broadcast' a packet to all other routers.
        """
        for port in self._outgoing_ports:
            try:
                # getsockname()[1] is the port
                self._socket.sendto(packet, (self._bind, port))
            except error:
                self._logger.critical("Socket send failed")
                sys.exit(1)

    def poll_incoming_ports(self):
        """
            Poll all incoming ports for available UDP packets
            To be called by scheduller
        """
        recieved_packets = []
        for event_socket, event in self._incoming_events:
            # self._incoming_events is always empty
            raise NotImplementedError  # continue from here
            # If we have received an event
            if not (event and select.POLLIN):
                return  # [] (useful to return None for debugging)

            # Check each of our registered sockets for a match
            for registered_socket in self._incoming_sockets:
                # If this isn't the socket we received data on, continue
                if event_socket == registered_socket.fileno():
                    continue

                # Otherwise, get data from the socket and return it
                self._logger.info(f'Recieved packet on port \
                                    {registered_socket.getsockname()[1]}')
                # likely need to change this 4096, and include the src port
                recieved_packets.append(registered_socket.recvfrom(4096))

        return recieved_packets


if __name__ == "__main__":
    INCOMING_PORTS = [8084, 8085]
    OUTGOING_PORTS = [8086, 8087]
    BIND = "127.0.0.1"
    interface1 = Interface(INCOMING_PORTS, OUTGOING_PORTS, BIND)
    interface2 = Interface(OUTGOING_PORTS, INCOMING_PORTS, BIND)

    interface1.broadcast(b'Hello!')
    time.sleep(1)
    data = []
    try:
        while data == []:
            data = interface1.poll_incoming_ports()
        print(data)
    except KeyboardInterrupt:
        interface1.close_sockets()
        interface2.close_sockets()
        sys.exit(1)

    interface1.close_sockets()
    interface2.close_sockets()
