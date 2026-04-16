"""マイコンへcanを送信するライブラリ"""

#!/usr/bin/env python3

import asyncio
import can
import time
import numpy as np
import struct

#
#  OPERATING_MODE_ADDR = 0,
#  GOAL_POS_ADDR = 1,
#  GOAL_VEL_ADDR = 2,
#  GOAL_PWM_ADDR = 3,
#  CURRENT_POS_ADDR = 4,
#  CURRENT_SPEED_ADDR = 5,
#  POS_P_ADDR = 6,
#  POS_I_ADDR = 7,
#  POS_D_ADDR = 8,
#  VEL_P_ADDR = 9,
#  VEL_I_ADDR = 10,
#  VEL_D_ADDR = 11,
#  AIR_ADDR = 12,
#
#
#  stop_mode = 0,
#  encoder_position_mode = 1,
#  potentio_position_mode = 2,
#  velocity_mode = 3,
#  pwm_mode = 4,
#  air_mode = 5,
#


def send_packet_1byte(can_id, table_addr, data, bus):
    """1byte送信
    1000はかけずに、そのまま送信する

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
    1000をかけて送信する、受信先で1000で割る

    Args:
        can_id
        table_addr コントロールテーブルアドレス
        data 1byte
        bus can_bus
    """

    data_int = int(data * 1000)
    byte1, byte2, byte3, byte4 = from_int32_to_bytes(data_int)
    packet = [table_addr, byte1, byte2, byte3, byte4]  #リトルエンディアン

    msg = can.Message(arbitration_id=can_id, data=packet, is_extended_id=False)
    bus.send(msg)


def from_int32_to_bytes(data):
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


def receive_frame(period, bus):
    recv_msg = bus.recv(timeout=period)

    if recv_msg is None:
        return None, None

    motor_id = (recv_msg.arbitration_id & 0x00F) - 4
    #print(motor_id)

    if motor_id < 0 or motor_id > 3:
        return None, None

    recv_data = ((recv_msg.data[3] << 24) | (recv_msg.data[2] << 16) |
                 (recv_msg.data[1] << 8) | (recv_msg.data[0]))

    if (recv_data is None):
        return None, None

    recv_data = struct.pack("<I", recv_data)
    recv_data = struct.unpack("<i", recv_data)[0]

    return recv_msg.arbitration_id - 4, recv_data


def set_stop_mode(can_id, bus):
    table_addr = 0
    data = 0

    send_packet_1byte(can_id, table_addr, data, bus)


def set_enc_pos_mode(can_id, bus):
    table_addr = 0
    data = 1

    send_packet_1byte(can_id, table_addr, data, bus)


def set_potentio_pos_mode(can_id, bus):
    table_addr = 0
    data = 2

    send_packet_1byte(can_id, table_addr, data, bus)


def set_enc_vel_mode(can_id, bus):
    table_addr = 0
    data = 3

    send_packet_1byte(can_id, table_addr, data, bus)


def set_pwm_mode(can_id, bus):
    table_addr = 0
    data = 4

    send_packet_1byte(can_id, table_addr, data, bus)


def set_air_mode(can_id, bus):
    table_addr = 0
    data = 5

    send_packet_1byte(can_id, table_addr, data, bus)


def set_goal_pos(can_id, data, bus):
    table_addr = 1
    send_packet_4byte(can_id, table_addr, data, bus)


def set_goal_vel(can_id, data, bus):
    table_addr = 2
    send_packet_4byte(can_id, table_addr, data, bus)


def set_goal_pwm(can_id, data, bus):
    table_addr = 3
    send_packet_4byte(can_id, table_addr, data, bus)


def set_air(can_id, data, bus):
    table_addr = 12
    send_packet_1byte(can_id, table_addr, data, bus)


def set_motor_rot_dir(can_id, data, bus):
    table_addr = 13
    send_packet_1byte(can_id, table_addr, data, bus)


def set_profile_vel(can_id, data, bus):
    table_addr = 14
    send_packet_4byte(can_id, table_addr, data, bus)


def set_profile_accel(can_id, data, bus):
    table_addr = 15
    send_packet_4byte(can_id, table_addr, data, bus)


def set_pos_pid_gain(can_id, p_gain, i_gain, d_gain, bus):
    send_packet_4byte(can_id, 6, p_gain, bus)  #p_gain
    send_packet_4byte(can_id, 7, i_gain, bus)  #i_gain
    send_packet_4byte(can_id, 8, d_gain, bus)  #d_gain


def set_vel_pid_gain(can_id, p_gain, i_gain, d_gain, bus):
    send_packet_4byte(can_id, 9, p_gain, bus)  #p_gain
    send_packet_4byte(can_id, 10, i_gain, bus)  #i_gain
    send_packet_4byte(can_id, 11, d_gain, bus)  #d_gain


def send_read_pos_instruction(can_id, bus):
    """角度　read命令を送信する"""

    current_pos_table_addr = 4

    packet = [current_pos_table_addr]
    msg = can.Message(arbitration_id=can_id, data=packet, is_extended_id=False)
    bus.send(msg)


def send_read_vel_instruction(can_id, bus):
    """速度　read命令を送信する"""

    current_vel_table_addr = 5

    packet = [current_vel_table_addr]
    msg = can.Message(arbitration_id=can_id, data=packet, is_extended_id=False)
    bus.send(msg)


def read_pos(can_id, bus):
    send_read_pos_instruction(can_id, bus)
    motor_id, recv_data = receive_frame(0.001, bus)
    if (motor_id is not can_id):

        return None, None
    return motor_id, recv_data / 1000.0


def read_vel(can_id, bus):
    send_read_vel_instruction(can_id, bus)
    motor_id, recv_data = receive_frame(0.001, bus)
    if (motor_id is not can_id):
        return None, None

    return motor_id, recv_data / 1000.0
