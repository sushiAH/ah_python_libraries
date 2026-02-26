import socket
import time
import struct


def init_udp():
    # ---- Config ----
    UDP_IP = "0.0.0.0"
    UDP_PORT = 12345

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    return sock


def udp_send(esp32_id, motor_id, table_addr, data, sock):
    ESP32_IP = "192.168.10." + str(esp32_id)
    ESP32_PORT = 8888
    packet_format = "<III"  # I=uint32_t

    binary_data = struct.pack(packet_format, motor_id, table_addr, data)
    sock.sendto(binary_data, (ESP32_IP, ESP32_PORT))


def udp_receive(packet_format, sock):
    data, addr = sock.recvfrom(1024)
    unpacked_data = struct.unpack(packet_format, data)

    return unpacked_data
