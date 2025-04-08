class IPTools:
    @staticmethod
    def ip_to_bytes(ip: str):
        """
            Convert an IP address to bytes.
        """
        chunks = ip.split('.')
        return bytes([int(chunk) for chunk in chunks])

    @staticmethod
    def bytes_to_ip(ip: bytes):
        """
            Convert bytes to an IP address.
        """
        return '.'.join([str(byte) for byte in ip])
