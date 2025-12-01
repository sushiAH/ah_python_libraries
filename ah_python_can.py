#!/usr/bin/env python3
import asyncio
import can
import time
import numpy as np
import struct
#addr
#operating mode 0
#goal_pos       1
#goal_vel       2
#pre_pos        3
#pre_vel        4

#operating mode 
#pos 1
#vel 2

def send_read_instruction(motor_id,table_addr,bus):
  packet = [table_addr]
  msg = can.Message(
    arbitration_id = motor_id,
    data=packet,
    is_extended_id = False)
  bus.send(msg)


def send_packet_1byte(motor_id,table_addr,data,bus):
  packet = [table_addr,data]
  msg = can.Message(
    arbitration_id = motor_id,
    data=packet,
    is_extended_id = False)
  bus.send(msg)

def send_packet_4byte(motor_id,table_addr,data,bus):
  byte1,byte2,byte3,byte4 = split_data_to_4byte(data)
  packet = [table_addr,byte1,byte2,byte3,byte4]

  msg = can.Message(
    arbitration_id = motor_id,
    data = packet,
    is_extended_id = False)
  bus.send(msg)

def split_data_to_4byte(data):
  byte1 = (data >> 24) & 0xFF  #最上位bit
  byte2 = (data >> 16) & 0xFF
  byte3 = (data >> 8) & 0xFF
  byte4 = (data) & 0xFF #最下位bit

  return byte1,byte2,byte3,byte4

    
