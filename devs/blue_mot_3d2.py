class Device(object):
    _gpib_address = "GPIB0::5::INSTR"
    _host = ('192.168.1.91', 42922)
    _slot = 1

    def __init__(self):
        if self._host is not None:
            from labd.libs._pyvisa import PyvisaProxy
            pyvisa = PyvisaProxy(self._host)
        else:
            import pyvisa

        rm = pyvisa.ResourceManager()
        self._inst = rm.open_resource(self._gpib_address)
    
    @property
    def output(self) -> bool:
        r = self._inst.query(f':SLOT {self._slot};:LASER?').strip()
        if r == ':LASER ON':
            return True
        elif r == ':LASER OFF':
            return False

    @output.setter
    def output(self, output: bool):
        if output:
            self._inst.write(f':SLOT {self._slot};:LASER ON')
        else: 
            self._inst.write(f':SLOT {self._slot};:LASER OFF')

    @property
    def current_setpoint(self) -> float:
        return float(self._inst.query(f':SLOT {self._slot};:ILD:SET?')[9:])

    @current_setpoint.setter
    def current_setpoint(self, current_setpoint: float):
        self._inst.write(f':SLOT {self._slot};:ILD:SET {current_setpoint}')

    @property
    def optical_power(self) -> float:
        return float(self._inst.query(f':SLOT {self._slot};:POPT:ACT?')[10:])

import os
import socket
import struct

def _comm(data, host=('localhost', 4292), timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(host)
    s.settimeout(timeout)
    s.send(data)
    r = s.recv(1024)
    return r 

class DeviceProxy(object):
    def __init__(self, inithost=('localhost', 4292)):
        self._inithost = inithost
        r = _comm(f'Ensure devs {os.path.basename(__file__)}'.encode(), inithost, timeout=10)
        self._devhost = inithost[0], int(r.decode())

    def __del__(self):
        r = _comm(f'STOP {self._libhost[1]}'.encode(), self._inithost)

    def _echo(self, message):
        r = _comm(f'_echo {message}'.encode(), self._devhost)
        return r.decode()

    @property
    def output(self):
        r = _comm(f'output_getattr'.encode(), self._devhost)
        return bool(int.from_bytes(r, 'big'))

    @output.setter
    def output(self, output):
        _comm(f'output_setattr {int(output)}'.encode(), self._devhost)
    
    @property
    def current_setpoint(self):
        r = _comm(f'current_setpoint_getattr'.encode(), self._devhost)
        return struct.unpack('>f', r)[0]

    @current_setpoint.setter
    def current_setpoint(self, current_setpoint):
        _comm(f'current_setpoint_setattr {current_setpoint}'.encode(), self._devhost)
    
    @property
    def optical_power(self):
        r = _comm(f'optical_power_getattr'.encode(), self._devhost)
        return struct.unpack('>f', r)[0]

def handle_request(conn):
    global dev
    data = conn.recv(1024)
    action, _, args = data.partition(b" ")
    print(__file__, action, args)
    
    if action == b"_echo":
        conn.send(args)
    elif action == b"output_getattr":
        conn.send(int(dev.output).to_bytes(1, 'big'))
    elif action == b"output_setattr":
        dev.output = bool(int(args))
        conn.send(b'')
    elif action == b'current_setpoint_getattr':
        conn.send(struct.pack('>f', float(dev.current_setpoint)))
    elif action == b'current_setpoint_setattr':
        dev.current_setpoint = float(args)
        conn.send(b'')
    elif action == b'optical_power_getattr':
        conn.send(struct.pack('>f', float(dev.optical_power)))


if __name__ == "__main__":
    import logging
    import sys

    dev = Device()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if len(sys.argv) == 2:
        s.bind(("0.0.0.0", 0))
        pid = sys.argv[1]
        port = s.getsockname()[1]
        stmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        stmp.connect(("localhost", 42922))
        stmp.send(f"PORT {pid} {port}".encode())
        s.listen(1)
    else:
        s.bind(("0.0.0.0", 65050))
        s.listen(1)

    while True:
        conn, addr = s.accept()
        handle_request(conn)
        conn.close()
