import socket
import threading
import random

def generate_mac_address():
    """Generate a random MAC address."""
    mac = [random.randint(0x00, 0xFF) for _ in range(6)]
    # Ensure that the first byte is even (to maintain uniqueness in certain cases)
    mac[0] = random.randint(0x00, 0xFE)  # Avoid multicast MAC addresses (even first bit)
    return ':'.join(['{:02x}'.format(octet) for octet in mac])

def generate_ip():
    """Generate a random IP address for the host"""
    return f"192.168.0.{random.randint(2, 254)}"

class VirtualHost:
    def __init__(self, switch_ip, switch_port, host_port):
        self.mac_address = generate_mac_address()
        self.ip_address = generate_ip()
        self.switch_ip = switch_ip
        self.switch_port = switch_port
        self.host_port = host_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("localhost", self.host_port))
        self.initiate_connection()
        print(f"Host {self.ip_address} initialized on port {self.host_port}")

    def initiate_connection(self):
        """Send a packet to the switch"""
        data = f"{self.ip_address}|{host_port}".encode()
        self.socket.sendto("connection", data, (self.switch_ip, self.switch_port))

    def send_packet(self, dst_ip, message):
        """Send a packet to the switch"""
        data = f"{self.mac_address}|{self.ip_address}|{dst_ip}|{message}".encode()
        self.socket.sendto(None, data, (self.switch_ip, self.switch_port))

    def listen_for_packets(self):
        """Listen for incoming packets"""
        while True:
            data, addr = self.socket.recvfrom(1024)
            src_mac, src_ip, dst_ip, payload = data.decode().split("|")
            print(f"Host {self.ip_address} received message from {src_ip} - {src_mac}: {payload}")

    def run(self):
        """Run the host to listen and send packets"""
        threading.Thread(target=self.listen_for_packets).start()


if __name__ == "__main__":
    switch_ip = "localhost"
    switch_port = 9000
    host_port = random.randint(10000, 11000)
    host = VirtualHost(switch_ip, switch_port, host_port)
    host.run()

    # Example communication
    while True:
        dst_ip = input("Enter destination IP address (or 'broadcast'): ")
        message = input("Enter message: ")
        if dst_ip.lower() == 'broadcast':
            host.send_packet("255.255.255.255", message)
        else:
            host.send_packet(dst_ip, message)
