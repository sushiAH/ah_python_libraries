#!/usr/bin/env python3
"""マイコンへcanを送信するライブラリ"""


import asyncio
import can
import time
import numpy as np
import struct

# addr
# operating mode 0
# goal_pos       1
# goal_vel       2
# pre_pos        3
# pre_vel        4

# operating mode
# pos 1
# vel 2


def send_read_vel_instruction(can_id, bus):
    """速度　read命令を送信する"""

    current_vel_table_addr = 4

    packet = [current_vel_table_addr]
    msg = can.Message(arbitration_id=can_id, data=packet, is_extended_id=False)
    bus.send(msg)


def send_read_pos_instruction(can_id, bus):
    """角度　read命令を送信する"""

    current_pos_table_addr = 3

    packet = [current_pos_table_addr]
    msg = can.Message(arbitration_id=can_id, data=packet, is_extended_id=False)
    bus.send(msg)


def send_packet_1byte(can_id, table_addr, data, bus):
    """1byte送信

    Args:
        can_id
        table_addr コントロールテーブルアドレス
        data 1byte
        bus can_bus
    """
    packet = [table_addr, data]
    msg = can.Message(arbitration_id=can_id, data=packet, is_extended_id=False)
    bus.send(msg)


def send_packet_4byte(can_id, table_addr, data, bus):
    """4byte送信

    Args:
        can_id
        table_addr コントロールテーブルアドレス
        data 1byte
        bus can_bus
    """
    byte1, byte2, byte3, byte4 = split_data_to_4byte(data)
    packet = [table_addr, byte1, byte2, byte3, byte4]

    msg = can.Message(arbitration_id=can_id, data=packet, is_extended_id=False)
    bus.send(msg)


def split_data_to_4byte(data):
    """リトルエンディアンでint32をバイト列に変換し、tupleで返す

    Args:
        data int32_value

    Returns: tuple 4byte

    """
    byte4 = (data >> 24) & 0xFF  # 最上位bit
    byte3 = (data >> 16) & 0xFF
    byte2 = (data >> 8) & 0xFF
    byte1 = (data) & 0xFF  # 最下位bit

    return (byte1, byte2, byte3, byte4)


def receive_frame(bus, period):
    recv_msg = bus.recv(timeout=period)
    if recv_msg != None:
        motor_id = recv_msg.arbitration_id - 20
        if motor_id >= 0 and motor_id <= 3:
            target = (
                (recv_msg.data[0] << 24)
                | (recv_msg.data[1] << 16)
                | (recv_msg.data[2] << 8)
                | (recv_msg.data[3])
            )
            target = struct.pack("<I", target)
            target = struct.unpack("<i", target)[0]
            data_array[motor_id] = target


def receive_frame(bus, period, data_array):
    recv_msg = bus.recv(timeout=period)

    if recv_msg == None:
        return None

    motor_id = recv_msg.arbitration_id - 20

    if not motor_id >= 0 and motor_id <= 3:
        return None

    target = (
        (recv_msg.data[0] << 24)
        | (recv_msg.data[1] << 16)
        | (recv_msg.data[2] << 8)
        | (recv_msg.data[3])
    )
    target = struct.pack("<I", target)
    target = struct.unpack("<i", target)[0]
    data_array[motor_id] = target
