import socket
import threading

class VirtualSwitch:
    def __init__(self, switch_port=9000):
        self.switch_port = switch_port
        self.ip_table = {}  # IP address table: {IP_address: (host_ip, host_port)}
        self.switch_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.switch_socket.bind(("localhost", self.switch_port))
        print(f"Switch initialized on port {self.switch_port}")

    def update_ip_table(self, mac, ip, addr):
        """Update the IP table with the IP address and sender's address"""
        if ip not in self.ip_table:
            print(f"Updating IP Table: {ip} -> {addr}")
        self.ip_table[ip] = (mac, addr)

    def handle_packet(self, data, addr):
        """Handle incoming packets and forward them"""
        src_mac, src_ip, dst_ip, payload = data.decode().split("|")
        print(f"Packet received from {src_mac} - {src_ip} to {dst_ip} with data: {payload}")

        # Update IP table with the source IP address
        self.update_ip_table(src_mac, src_ip, addr)

        # Forward packet to the destination
        if dst_ip in self.ip_table:
            _, dst_addr = self.ip_table[dst_ip]
            self.switch_socket.sendto(data, dst_addr)
            print(f"Forwarding packet to {dst_ip} at {dst_addr}")
        else:
            # Broadcast to all known hosts if destination is unknown
            print(f"Unknown IP: Broadcasting to all hosts")
            for host_addr in self.ip_table.values():
              _, h_addr = self.ip_table[src_ip]
              print(h_addr)
              if h_addr != addr:  # Avoid sending back to the sender
                  self.switch_socket.sendto(data, h_addr)

    def listen_for_connection_requests(self, data, addr):
        """Listen for incoming connection requests from hosts"""
        
        data, addr = self.switch_socket.recvfrom(1024)
        print(f"Connection request received from {addr}")
        ip, host_port = data.decode().split("|")
        print(f"Host IP: {ip}, Host Port: {host_port}")

        # Update the switch's IP table with the new host
        self.update_ip_table(None, ip, addr)  # No MAC address yet, just the IP and port

        # Optionally, send a confirmation back to the host
        self.switch_socket.sendto(f"Received connection from {ip}".encode(), addr)

    def run(self):
        """Start the switch to listen for incoming packets"""
        print("Virtual Switch is running...")
        try:
            while True:
                isConnection, data, addr = self.switch_socket.recvfrom(1024)
                print('addr: ', addr)
                if isConnection:
                  threading.Thread(target=self.listen_for_connection_requests, args=(data, addr)).start()  # Start connection listener thread
                else:
                  threading.Thread(target=self.handle_packet, args=(data, addr)).start()
        except KeyboardInterrupt:
            print("Switch shutting down...")
        finally:
            self.switch_socket.close()


if __name__ == "__main__":
    vswitch = VirtualSwitch()
    vswitch.run()
