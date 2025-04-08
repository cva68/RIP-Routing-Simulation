"""
    Exceptions for the ripd module.
    Authors: C. Varney, K. Jones
"""


class PacketParseError(Exception):
    """Exception raised for errors encountered while parsing a packet."""
    def __init__(self, message="Error occurred while parsing the packet"):
        super().__init__(message)
