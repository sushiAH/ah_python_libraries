# usr/bin/env python3
import os
import struct
from dynamixel_sdk import *  # Uses Dynamixel SDK library


# ********* DYNAMIXEL Model definition *********
# ***** (Use only one definition at a time) *****
MY_DXL = "X_SERIES"  # X330 (5.0 V recommended), X430, X540, 2X430
# MY_DXL = 'MX_SERIES'    # MX series with 2.0 firmware update.
# MY_DXL = 'PRO_SERIES'   # H54, H42, M54, M42, L54, L42
# MY_DXL = 'PRO_A_SERIES' # PRO series with (A) firmware update.
# MY_DXL = 'P_SERIES'     # PH54, PH42, PM54
# MY_DXL = 'XL320'        # [WARNING] Operating Voltage : 7.4V

# Control table address
if MY_DXL == "X_SERIES" or MY_DXL == "MX_SERIES":
    ADDR_TORQUE_ENABLE = 64
    ADDR_GOAL_POSITION = 116
    ADDR_GOAL_VELOCITY = 104
    ADDR_PRESENT_POSITION = 132
    ADDR_PRESENT_VELOCITY = 128
    ADDR_POS_P_GAIN = 84
    ADDR_GOAL_PWM = 100
    ADDR_CHANGE_MODE = 11
    ADDR_ID = 8

    DXL_MINIMUM_POSITION_VALUE = (
        0  # Refer to the Minimum Position Limit of product eManual
    )
    DXL_MAXIMUM_POSITION_VALUE = (
        4095  # Refer to the Maximum Position Limit of product eManual
    )
    BAUDRATE = 115200

    LEN_GOAL_POSITION = 4


elif MY_DXL == "PRO_SERIES":
    ADDR_TORQUE_ENABLE = 562  # Control table address is different in DYNAMIXEL model
    ADDR_GOAL_POSITION = 596
    ADDR_PRESENT_POSITION = 611
    DXL_MINIMUM_POSITION_VALUE = (
        -150000
    )  # Refer to the Minimum Position Limit of product eManual
    DXL_MAXIMUM_POSITION_VALUE = (
        150000  # Refer to the Maximum Position Limit of product eManual
    )
    BAUDRATE = 57600
elif MY_DXL == "P_SERIES" or MY_DXL == "PRO_A_SERIES":
    ADDR_TORQUE_ENABLE = 512  # Control table address is different in DYNAMIXEL model
    ADDR_GOAL_POSITION = 564
    ADDR_PRESENT_POSITION = 580
    DXL_MINIMUM_POSITION_VALUE = (
        -150000
    )  # Refer to the Minimum Position Limit of product eManual
    DXL_MAXIMUM_POSITION_VALUE = (
        150000  # Refer to the Maximum Position Limit of product eManual
    )
    BAUDRATE = 57600
elif MY_DXL == "XL320":
    ADDR_TORQUE_ENABLE = 24
    ADDR_GOAL_POSITION = 30
    ADDR_PRESENT_POSITION = 37
    DXL_MINIMUM_POSITION_VALUE = 0  # Refer to the CW Angle Limit of product eManual
    DXL_MAXIMUM_POSITION_VALUE = 1023  # Refer to the CCW Angle Limit of product eManual
    BAUDRATE = 1000000  # Default Baudrate of XL-320 is 1Mbps


def goal_pos_to_4byte(goal_pos):
    param_goal_position = [
        DXL_LOBYTE(DXL_LOWORD(goal_pos)),
        DXL_HIBYTE(DXL_LOWORD(dxl_goal_position)),
        DXL_LOBYTE(DXL_HIWORD(dxl_goal_position)),
        DXL_HIBYTE(DXL_HIWORD(dxl_goal_position)),
    ]
    return param_goal_position


class dxl_controller:
    """dynamixel controller class"""

    def __init__(self, port_name, dxl_id, mode):
        PROTOCOL_VERSION = 2.0

        self.portHandler = PortHandler(port_name)
        self.packetHandler = PacketHandler(PROTOCOL_VERSION)
        self.groupSyncWrite = GroupSyncWrite(
            self.portHandler, self.packetHandler, ADDR_GOAL_POSITION, LEN_GOAL_POSITION
        )

        self.dxl_id = dxl_id

        self.portHandler.openPort()
        self.portHandler.setBaudRate(BAUDRATE)

        self.set_torque(0)
        self.set_mode(mode)
        self.set_torque(1)

    def set_torque(self, torque):
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
            self.portHandler, self.dxl_id, ADDR_TORQUE_ENABLE, torque
        )
        return dxl_comm_result, dxl_error

    def set_mode(self, dyna_mode):
        """dyna_mode     value
            vel         1
            pos         3
        extended pos    4
        """

        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
            self.portHandler, self.dxl_id, ADDR_CHANGE_MODE, dyna_mode
        )
        return dxl_comm_result, dxl_error

    def write_pos(self, goal_pos):
        # absolute goal_pos range is 0 ~ 4095
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(
            self.portHandler, self.dxl_id, ADDR_GOAL_POSITION, goal_pos
        )
        return dxl_comm_result, dxl_error

    def write_vel(self, goal_vel):
        # goal_vel range is 0~1023
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(
            self.portHandler, self.dxl_id, ADDR_GOAL_VELOCITY, goal_vel
        )
        return dxl_comm_result, dxl_error

    def write_pos_pid(self, p_gain):
        dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(
            self.portHandler, self.dxl_id, ADDR_POS_P_GAIN, p_gain
        )
        return dxl_comm_result, dxl_error

    def add_sync_param(self, goal_pos):
        param_goal_pos = goal_pos_to_4byte(goal_pos)
        self.groupSyncWrite.addParam(self.dxl_id, param_goal_pos)

    def write_group_dyna(self):
        self.groupSyncWrite.txPacket()
        self.groupSyncWrite.clearParam()

    def write_goal_pwm(self, goal_pwm):
        dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(
            self.portHandler, self.dxl_id, ADDR_GOAL_PWM, goal_pwm
        )
        return dxl_comm_result, dxl_error

    def read_pos(self):
        dxl_present_position, dxl_comm_result, dxl_error = (
            self.packetHandler.read4ByteTxRx(
                self.portHandler, self.dxl_id, ADDR_PRESENT_POSITION
            )
        )
        return dxl_present_position

    def read_vel(self):
        dxl_present_velocity, dxl_comm_result, dxl_error = (
            self.packetHandler.read4ByteTxRx(
                self.portHandler, self.dxl_id, ADDR_PRESENT_VELOCITY
            )
        )
        return dxl_present_velocity

    def close_port(self):
        self.portHandler.closePort()
