"""esp32から、feedbackデータのパケットを受け取り、publishする"""

import serial
import time
import struct
import numpy as np


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


def receive_packet(packet_len, ser):
    """esp32からパケットを受け取る

    Args:
        packet_len (int): パケット長さ
        ser (Serial): シリアルインスタンス


    Returns:
        bytes | None: 受信パケットデータ。エラー時 None
    """
    PACKET_STRUCT_FORMAT = "<BIfffffffffB"
    HEADER = 0xAA

    # headerの受取
    recv_header = ser.read(1)
    if len(recv_header) < 1:
        print("headerが受け取れていません")
        return None
    if recv_header[0] != HEADER:
        print("headerが誤っています", recv_header[0])
        return None

    # header以外のデータ受取
    remaining_data_len = packet_len - 1
    remaining_data = ser.read(remaining_data_len)

    # データ長の確認
    if len(remaining_data) < remaining_data_len:
        print("データ長が短いです")
        return None

    # packetの結合
    full_packet_bin = recv_header + remaining_data

    # checksum
    checksum_val = calc_checksum(full_packet_bin)
    if checksum_val != 0:
        print("チェックサムが正しくありません", checksum_val)
        return None

    # binaryから変換
    packet = struct.unpack(PACKET_STRUCT_FORMAT, full_packet_bin)

    return packet
