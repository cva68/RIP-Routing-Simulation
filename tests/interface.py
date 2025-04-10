"""
    Unit tests for the interface module.
    Author: C. Varney, K. Jones
"""

import unittest
import time

from context import Interface

INCOMING_PORTS = [8080, 8081]
OUTGOING_PORTS = [8082, 8083]
BIND = "127.0.0.1"


class InterfaceTestSuite(unittest.TestCase):
    """
        Interface test suite.
    """
    # def test_initialisation(self):
    #     """
    #         Test the initialisation of a RIP entry.
    #     """
    #     interface1 = Interface(INCOMING_PORTS, OUTGOING_PORTS, BIND)
    #     self.assertIsNotNone(interface1)
    #     interface1.close_sockets()
    
    def test_broadcast_and_recieve(self):
        """
            Initialise two sockets, broadcast on one, and recieve on one.
        """
        interface1 = Interface(INCOMING_PORTS, OUTGOING_PORTS, BIND)
        interface2 = Interface(OUTGOING_PORTS, INCOMING_PORTS, BIND)

        interface1.broadcast(b'Hello!')
        time.sleep(1)
        data = interface1.poll_incoming_ports()
        print(data)

        interface1.close_sockets()
        interface2.close_sockets()


if __name__ == '__main__':
    unittest.main()
