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
        return bool(int(self._inst.query('OUTPUT:STATE?').strip()))

    @output.setter
    def output(self, output: bool):
        if output:
            self._inst.write('OUTPUT:STATE ON')
        else: 
            self._inst.write('OUTPUT:STATE OFF')

import socket

def _comm(data, host=('localhost', 4292), timeout=0.1):
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

#import socket
#
#def _comm(data, host=('localhost', 4292), timeout=10):
#    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    s.connect(host)
#    s.settimeout(timeout)
#    s.send(data)
#    r = s.recv(1024)
#    return r 
#
#class VisaProxy(object):
#    def __init__(self, inithost=('localhost', 4292)):
#        self._inithost = inithost
#        r = _comm('START libs _visa.py'.encode(), inithost)
#        self._libhost = inithost[0], int(r.decode())
#
#    def __del__(self):
#        r = _comm(f'STOP {self._libhost[1]}'.encode(), self._inithost)
#
#    def _echo(self, message):
#        r = _comm(f'_echo {message}'.encode(), self._libhost)
#        return r.decode()
#
#    def ResourceManager(self):
#        return ResourceManagerProxy(self._libhost)
#
#class ResourceManagerProxy(object):
#    def __init__(self, host):
#        self._host = host
#
#    def list_resources(self, query='?*::INSTR'):
#        """ Return a tuple of all connected devices matching query.
#        
#        Parameters:
#            query (str) : VISA Resource Regular Expression syntax 
#        Returns:
#            (tuple) connected devices matching query
#        """
#        r = _comm(f'list_resources {query}'.encode(), self._host)
#        return r.decode()
#
#    def open_resource(self, resource_name, open_timeout=0, **kwargs):
#        """ Return an instrument for the resource name.
#
#        Parameters: 
#            resource_name (str): Name or alias of the resource to open.
#            open_timeout (int, optional): If the access_mode parameter 
#                requests a lock, then this parameter specifies the absolute 
#                time period (in milliseconds) that the resource waits to get 
#                unlocked before this operation returns an error, by default 
#                constants.VI_TMO_IMMEDIATE.
#            kwargs (Any) – Keyword arguments to be used to change instrument 
#            attributes after construction.
#        Returns:    
#            Subclass of Resource matching the resource.
#        """
#        r = _comm(f'open_resource {resource_name} {open_timeout} {kwargs}'.encode(),
#                  self._host)
#        if 'GPIB' in resource_name:
#            return GPIBInstrumentProxy(self._host, resource_name)
#        else:
#            raise Exception('resource type not supported :(')
#
#class GPIBInstrumentProxy(object):
#    def __init__(self, host, resource_name):
#        self._host = host
#        self._resource_name = resource_name
#
#    def control_ren(self, mode):
#        """ Controls the state of the GPIB Remote Enable (REN) interface line.
#
#        The remote/local state of the device can also be controlled optionally.
#        Corresponds to viGpibControlREN function of the VISA library.
#
#        Parameters: 
#            mode (constants.RENLineOperation) - Specifies the state of the REN 
#                line and optionally the device remote/local state.
#        Returns:    
#            Return value of the library call.
#        """
#        r = _comm(f'control_ren {mode}'.encode(), self._host)
#        return int.from_bytes(r, 'big')
#
#    def query(self, message, delay=None):
#        """A combination of write(message) and read()
#
#        Parameters:
#            message (str): the message to send.
#            delay (float): delay in seconds between write and read operations.
#                if None, defaults to self.query_delay
#        Returns:
#            (str) the answer from the device.
#        """
#        r = _comm(f'query {message} {delay}'.encode(), self._host)
#        return r.decode()
#
#    def read(self, termination=None, encoding=None):
#        """Read a string from the device.
#
#        Reading stops when the device stops sending (e.g. by setting appropriate 
#        bus lines), or the termination characters sequence was detected.
#        Attention: Only the last character of the termination characters is 
#        really used to stop reading, however, the whole sequence is compared to 
#        the ending of the read string message. If they don't match, a warning is 
#        issued.
#
#        All line-ending characters are stripped from the end of the string.
#        Parameters:
#            termination (str): characters at which to stop reading
#            encoding (str): encoding used for read operation
#        Returns:
#            (str) output from device
#        """
#        r = _comm(f'read {termination} {encoding}'.encode(), self._host)
#        return r.decode()
#
#    @property
#    def timeout(self):
#        """ The timeout in milliseconds for all resource I/O operations. """
#        r = _comm(f'timeout_getattr'.encode(), self._host)
#        return int.from_bytes(r, 'big')
#
#    @timeout.setter
#    def timeout(self, timeout):
#        """ The timeout in milliseconds for all resource I/O operations. """
#        _comm(f'timeout_setattr {timeout}'.encode(), self._host)
#
#    def write(self, message, termination=None, encoding=None):
#        """ Write a string message to the device.
#
#        The write_termination is always appended to it.
#
#        Parameters:
#            message (str): the message to be sent.
#            termination (str): termination chars to be appended to message.
#            encoding (str): byte encoding for message
#        Returns:
#            (int) number of bytes written
#        """
#        r = _comm(f'write {message} {termination} {encoding}'.encode(),
#                  self._host)
#        return int.from_bytes(r, 'big')
