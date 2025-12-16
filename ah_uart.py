"""uart通信プロトコルライブラリ
パケット構造
  header : 1byte
  packet_length : 1byte
"""

import time
import serial
import struct
import numpy as np


def send_4value_by_one_packet(table_addr, target_1, target_2, target_3, target_4, ser):
    """4つの値を一つのパケットにまとめてuart通信で送信する

    Args:
        table_addr コントロールテーブルアドレス
        target_1 値1
        target_2 値2
        target_3 値3
        target_4 値4
        ser シリアルインスタンス
    """
    header = 0xAA
    data_length = 21
    target_1 = int(target_1 * 1000)
    target_2 = int(target_2 * 1000)
    target_3 = int(target_3 * 1000)
    target_4 = int(target_4 * 1000)

    # int32をバイト列に変換
    byte_array_1 = from_int32_to_bytes(target_1)
    byte_array_2 = from_int32_to_bytes(target_2)
    byte_array_3 = from_int32_to_bytes(target_3)
    byte_array_4 = from_int32_to_bytes(target_4)

    packet = (
        [header, data_length, 0, table_addr]
        + byte_array_1
        + byte_array_2
        + byte_array_3
        + byte_array_4
    )

    check_sum_val = calc_checksum(packet)
    packet.append(check_sum_val)

    ser.write(bytes(packet))


# 1byte送信用
def send_packet_1byte(motor_id, table_addr, data, ser):
    header = 0xAA
    data_length = 6

    packet = [header, data_length, motor_id, table_addr, data]
    check_sum_val = calc_checksum(packet)
    packet.append(check_sum_val)

    ser.write(bytes(packet))


# 4byte送信用
def send_packet_4byte(motor_id, table_addr, data, ser):  # mode 1 is vel 2 is pos
    data_int = int(data * 1000)
    header = 0xAA
    data_length = 9
    byte_array = from_int32_to_bytes(data_int)

    # リトルエンディアン
    packet = [
        header,
        data_length,
        motor_id,
        table_addr,
        byte_array[0],
        byte_array[1],
        byte_array[2],
        byte_array[3],
    ]

    check_sum_val = calc_checksum(packet)
    packet.append(check_sum_val)

    ser.write(bytes(packet))


# read命令を送信
def send_read_instruction(motor_id, table_addr, ser):
    header = 0xAA
    data_length = 5
    packet = [header, data_length, motor_id, table_addr]
    check_sum_val = calc_checksum(packet)
    packet.append(check_sum_val)
    ser.write(bytes(packet))


def from_int32_to_bytes(value):
    """int32を、リトルエンディアン形式のバイトリストに変換する。

    Args:
        value (int32): 変換対象値

    Returns:
        list[int]: リトルエンディアン形式バイトリスト
    """
    byte4 = (value >> 24) & 0xFF  # 最上位byte
    byte3 = (value >> 16) & 0xFF
    byte2 = (value >> 8) & 0xFF
    byte1 = (value) & 0xFF  # 最下位byte

    return [byte1, byte2, byte3, byte4]


def calc_checksum(packet_data):
    """排他的論理和チェックサムを計算する

    Args:
        packet_data (Iterable[int]): パケットデータ

    Returns:
        チェックサム値
    """
    checksum_val = 0
    for i in range(0, len(packet_data)):
        checksum_val ^= packet_data[i]
    return checksum_val


def receive_packet(data_array, ser):
    """受け取ったidのデータを、data_arrayに格納する

    Args:
        data_array (byte): 各idのデータを格納するリスト (id : 0-3)
        ser シリアルインスタンス

    Returns:
        void

    """
    header = 0xAA
    target = None

    # headerの受取
    recv_header = ser.read(1)
    if len(recv_header) < 1 or recv_header[0] != header:
        return None

    # length_byteの受取
    length_byte = ser.read(1)
    if len(length_byte) < 1:
        return None
    recv_packet_length = length_byte[0]

    # 残りのデータ長を計算
    data_to_read = recv_packet_length - 3
    if data_to_read < 0:
        return None

    # motor_idの受取
    rx_motor_id = ser.read(1)
    if len(rx_motor_id) < 1:
        return None
    recv_id = rx_motor_id[0]
    if recv_id > 3 or recv_id < 0:
        if data_to_read > 0:
            ser.read(data_to_read)
        return None

    # その他データの受取
    if data_to_read <= 0:
        return None
    remaining_data = ser.read(data_to_read)
    if len(remaining_data) != data_to_read:
        return None

    # データの結合
    full_packet = recv_header + length_byte + rx_motor_id + remaining_data

    # チェックサム
    calculated_checksum = calc_checksum(full_packet)
    if calculated_checksum != 0:
        return None

    # リトルエンディアンにしたがって、byte列からint32を作成する
    target = (
        (full_packet[6] << 24)
        | (full_packet[5] << 16)
        | (full_packet[4] << 8)
        | (full_packet[3])
    )

    target = struct.pack("<I", target)
    target = struct.unpack("<i", target)[0]

    data_array[recv_id] = target / 1000.000


def sync_write():
    pass


def sync_read():
    pass
