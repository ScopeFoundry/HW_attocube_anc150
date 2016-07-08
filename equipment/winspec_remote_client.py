
import socket
import time
import struct
from array import array
from matplotlib import pyplot as plt

import ctypes as ct

class data_header(ct.Structure):
    _pack_ = 1
    _fields_ = [
        ('total_size', ct.c_int32),
        ('data_type', ct.c_int32),
        ('xdim', ct.c_int32),
        ('ydim', ct.c_int32),
        ('intg_time', ct.c_double),
        ('grating_pos', ct.c_double),
        ('calib_coeffs', ct.c_double*5),
        ('frame_count', ct.c_int32),
        ('data_size', ct.c_int32),
        ]

class WinSpecRemoteClient(object):

    def __init__(self, host="192.168.254.200", port=9000, debug=True):
    
        s = self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def send_cmd(self, cmd):
        self.sock.send( ( cmd + "\n").encode('utf-8'))

    def ask_cmd(self, cmd):
        self.send_cmd(cmd)
        self.sock.recv()

    def set_acq_time(self, t):
        