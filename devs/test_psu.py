class Device(object):
    _gpib_address = "GPIB0::5::INSTR"
    _host = None
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
        return bool(int(self._inst.query('OUTP?').strip()))

    @output.setter
    def output(self, output: bool):
        if output:
            self._inst.write('OUTP ON')
        else: 
            self._inst.write('OUTP OFF')

    @property
    def voltage_setpoint(self) -> float:
        return float(self._inst.query('VOLT?').strip())

    @voltage_setpoint.setter
    def voltage_setpoint(self, voltage_setpoint: float):
        self._inst.write(f'VOLT {voltage_setpoint}')
    
    @property
    def measured_voltage(self) -> float:
        return float(self._inst.query('MEAS:VOLT?').strip())

    @property
    def current_setpoint(self) -> float:
        return float(self._inst.query('CURR?').strip())

    @current_setpoint.setter
    def current_setpoint(self, current_setpoint: float):
        self._inst.write(f'CURR {current_setpoint}')
    
    @property
    def measured_current(self) -> float:
        return float(self._inst.query('MEAS:CURR?').strip())


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
        r = _comm('Ensure devs test_psu.py'.encode(), inithost, timeout=10)
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
    def voltage_setpoint(self):
        r = _comm(f'voltage_setpoint_getattr'.encode(), self._devhost)
        return struct.unpack('>f', r)[0]

    @voltage_setpoint.setter
    def voltage_setpoint(self, voltage_setpoint):
        _comm(f'voltage_setpoint_setattr {voltage_setpoint}'.encode(), self._devhost)
    
    @property
    def measured_voltage(self):
        r = _comm(f'measured_voltage_getattr'.encode(), self._devhost)
        return struct.unpack('>f', r)[0]
    
    @property
    def current_setpoint(self):
        r = _comm(f'current_setpoint_getattr'.encode(), self._devhost)
        return struct.unpack('>f', r)[0]

    @current_setpoint.setter
    def current_setpoint(self, current_setpoint):
        _comm(f'current_setpoint_setattr {current_setpoint}'.encode(), self._devhost)
    
    @property
    def measured_current(self):
        r = _comm(f'measured_current_getattr'.encode(), self._devhost)
        return struct.unpack('>f', r)[0]

def handle_request(conn):
    global dev
    data = conn.recv(1024)
    action, _, args = data.partition(b" ")

    print(__file__, action, args)
    
    if action == b"_echo":
        conn.send(args)
    elif action == b"output_getattr":
        output = dev.output
        conn.send(int(output).to_bytes(1, 'big'))
    elif action == b"output_setattr":
        output = int(args) 
        dev.output = output
        conn.send(b'')
    elif action == b'voltage_setpoint_getattr':
        voltage_setpoint = dev.voltage_setpoint
        conn.send(struct.pack('>f', float(voltage_setpoint)))
    elif action == b'voltage_setpoint_setattr':
        voltage_setpoint = float(args)
        dev.voltage_setpoint = voltage_setpoint
        conn.send(b'')
    elif action == b'measured_voltage_getattr':
        measured_voltage = dev.measured_voltage
        conn.send(struct.pack('>f', float(measured_voltage)))
    elif action == b'current_setpoint_getattr':
        current_setpoint = dev.current_setpoint
        conn.send(struct.pack('>f', float(current_setpoint)))
    elif action == b'current_setpoint_setattr':
        current_setpoint = float(args)
        dev.current_setpoint = current_setpoint
        conn.send(b'')
    elif action == b'measured_current_getattr':
        measured_current = dev.measured_current
        conn.send(struct.pack('>f', float(measured_current)))


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
