"""
    Unit tests for the interface module.
    Author: C. Varney, K. Jones
"""

import unittest

from context import Interface

# Define some ports for test routers
INTERFACE1_INCOMING_PORTS = [8080, 8081, 8082]
INTERFACE2_INCOMING_PORTS = [8083, 8084, 8085]
INTERFACE3_INCOMING_PORTS = [8086, 8087, 8088]
INTERFACE1_OUTGOING_PORTS = [8080, 8083, 8086]
INTERFACE2_OUTGOING_PORTS = [8081, 8084, 8087]
INTERFACE3_OUTGOING_PORTS = [8082, 8085, 8088]
BIND = "127.0.0.1"


class InterfaceTestSuite(unittest.TestCase):
    """
        Interface test suite.
    """
    def test_initialisation(self):
        """
            Test the initialisation of a RIP entry.
        """
        interface1 = Interface(INTERFACE1_INCOMING_PORTS,
                               INTERFACE1_OUTGOING_PORTS,
                               BIND)
        self.assertIsNotNone(interface1)
        interface1.close_sockets()
    
    def test_broadcast_and_recieve(self):
        """
            Initialise three sockets, broadcast on one, and recieve on two.
        """
        interface1 = Interface(INTERFACE1_INCOMING_PORTS,
                               INTERFACE1_OUTGOING_PORTS,
                               BIND)
        interface2 = Interface(INTERFACE2_INCOMING_PORTS,
                               INTERFACE2_OUTGOING_PORTS,
                               BIND)
        interface3 = Interface(INTERFACE3_INCOMING_PORTS,
                               INTERFACE3_OUTGOING_PORTS,
                               BIND)

        # 'Broadcast' on interface 1
        interface1.broadcast(b'Hello!')

        # Recieve data
        data2, data3 = [], []
        try:
            while data2 == []:
                data2 = interface2.poll_incoming_ports()
            while data3 == []:
                data3 = interface3.poll_incoming_ports()

        except Exception as e:
            # Ensure sockets are closed, even when exiting on error
            interface1.close_sockets()
            interface2.close_sockets()
            interface3.close_sockets()
            raise e

        # Ensure received data was correct
        self.assertEqual(data2[0][0], b'Hello!')
        self.assertEqual(data3[0][0], b'Hello!')

        # Ensure each interface received just one packet
        self.assertEqual(len(data2), 1)
        self.assertEqual(len(data3), 1)

        # Close sockets
        interface1.close_sockets()
        interface2.close_sockets()
        interface3.close_sockets()


if __name__ == '__main__':
    unittest.main()
