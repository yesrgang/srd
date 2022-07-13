import socket

def _comm(data, host=('localhost', 4292), timeout=10):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(host)
    s.settimeout(timeout)
    s.send(data)
    r = s.recv(1024)
    return r 


class OKProxy(object):
    def __init__(self, inithost=('localhost', 4292)):
        self._inithost = inithost
        r = _comm('START libs _ok.py'.encode(), inithost)
        self._libhost = inithost[0], int(r.decode())

    def __del__(self):
        r = _comm(f'STOP {self._libhost[1]}'.encode(), self._inithost)


    def okCFrontPanel(self):
        """ This class is the workhorse of the FrontPanel API. 
        
        It's methods are organized into three main groups: Device Interaction, 
        Device Configuration, and FPGA Communication. In a typical application, 
        your software will perform the following steps:
        
        1. Create an instance of okCFrontPanel.
        2. Using the Device Interaction methods, find an appropriate XEM with which 
        to communicate and open that device.
        3. Configure the device PLL (for devices with an on-board PLL).
        4. Download a configuration file to the FPGA using ConfigureFPGA(...).
        5. Perform any application-specific communication with the FPGA using the 
        FPGA Communication methods.    
        """
        return okFrontPanelProxy(self._libhost)

    def okCFrontPanelDevices(self, realm=''):
        """ Enumerates all the devices available in the given realm. 
    
        The realm of the devices represented by this object. By default, i.e. if
        the value of this argument is an empty string, the realm specified by 
        the okFP_REALM environment variable is used or, if this variable is not 
        defined, the "local" realm.
        """
        return okCFrontPanelDevicesProxy(self._libhost, realm)

class okCFrontPanelDevicesProxy(object):
    """ Enumerates all the devices available in the given realm. 
   
    The realm of the devices represented by this object. By default, i.e. if 
    the value of this argument is an empty string, the realm specified by 
    the okFP_REALM environment variable is used or, if this variable is not 
    defined, the "local" realm.
    """
    def __init__(self, host, realm=''):
        self._host = host
        self._realm = realm

    def GetCount(self):
        """ Returns the number of available devices, possibly 0. """
        r = _comm(f'GetCount'.encode(), self._host)
        return int.from_bytes(r, 'big')

    def GetSerial(self, num=None):
        """ Returns the serial number of the given device, possibly empty if the 
        index is invalid."""
        r = _comm(f'GetSerial {num}'.encode(), self._host)
        return r.decode()

    def Open(self, serial=None):
        """ Opens the device with the given serial number, first one by default. 
        
        Returns an empty pointer if there is no such device (or no devices at 
        all if the serial is empty).
        """
        r = _comm(f'Open {serial}'.encode(), self._host)
        return okCFrontPanelProxy(self._host)

class okCFrontPanelProxy(object):
    """ This class is the workhorse of the FrontPanel API. 
    
    It's methods are organized into three main groups: Device Interaction, 
    Device Configuration, and FPGA Communication. In a typical application, 
    your software will perform the following steps:
    
    1. Create an instance of okCFrontPanel.
    2. Using the Device Interaction methods, find an appropriate XEM with which 
    to communicate and open that device.
    3. Configure the device PLL (for devices with an on-board PLL).
    4. Download a configuration file to the FPGA using ConfigureFPGA(...).
    5. Perform any application-specific communication with the FPGA using the 
    FPGA Communication methods.    
    """
    def __init__(self, host):
        self._host = host

    def Close(self):
        """ Close the device.
    
        This method can be used to close the device to release the corresponding 
        device at the system level, e.g. to allow another process to use it, 
        without destroying this object itself but keeping it to be reopened later.
        """
        r = _comm(f'Close'.encode(), self._host)

    def ConfigureFPGA(self, strFilename):
        """ Download an FPGA configuration from a file.
        
        Args:
            strFilename	(str): A string containing the filename of the 
                configuration file.
        """
        r = _comm(f'ConfigureFPGA {strFilename}'.encode(), self._host)
        return int.from_bytes(r, 'big')
    
    def GetWireInValue(self, epAddr):
        """ Gets the value of a particular Wire In from the internal wire data 
        structure.

        Args:
            epAddr (int): The WireIn address to query.
        """
        r = _comm(f'GetWireInValue {epAddr}'.encode(), self._host)
        return int.from_bytes(r, 'big')
    
    def GetWireOutValue(self, epAddr):
        """ Gets the value of a particular Wire Out from the internal wire data 
        structure.

        Args:
            epAddr (int): The WireOut address to query.
        """
        r = _comm(f'GetWireOutValue {epAddr}'.encode(), self._host)
        return int.from_bytes(r, 'big')
    
    def IsTriggered(self, epAddr, mask):
        """ Returns true if the trigger has been triggered.

        This method provides a way to find out if a particular bit (or bits) on 
        a particular TriggerOut endpoint has triggered since the last call to 
        UpdateTriggerOuts().

        Args:
            epAddr (int): The TriggerOut address to query.
            mask (int): A mask to apply to the trigger value.
        """
        r = _comm(f'IsTriggered {epAddr} {mask}'.encode(), self._host)
        return int.from_bytes(r, 'big')

    def SetWireInValue(self, epAddr, val, mask=0xffffffff):
        """ Sets a wire value in the internal wire data structure.

        WireIn endpoint values are stored internally and updated when necessary 
        by calling UpdateWireIns(). The values are updated on a per-endpoint 
        basis by calling this method. In addition, specific bits may be updated 
        independent of other bits within an endpoint by using the optional mask.

        Args:
            epAddr (int): The address of the WireIn endpoint to update.
            val (int): The new value of the WireIn.
            mask (int): A mask to apply to the new value
        """
        r = _comm(f'SetWireInValue {epAddr} {val} {mask}'.encode(), self._host)
        return int.from_bytes(r, 'big')

    def UpdateTriggerOuts(self):
        """ Reads Trigger Out endpoints. 
        
        This method is called to query the XEM to determine if any TriggerOuts 
        have been activated since the last call.
        """
        r = _comm(f'UpdateTriggerOuts'.encode(), self._host)
        return int.from_bytes(r, 'big')

    def UpdateWireIns(self):
        """ Transfers current Wire In values to the FPGA.

        This method is called after all WireIn values have been updated using 
        SetWireInValue(). The latter call merely updates the values held within 
        a data structure inside the class. This method actually commits the 
        changes to the XEM simultaneously so that all wires will be updated at 
        the same time.
        """
        r = _comm(f'UpdateWireIns'.encode(), self._host)
        return int.from_bytes(r, 'big')
    
    def UpdateWireOuts(self):
        """ Transfers current Wire Out values from the FPGA.

        This method is called to request the current state of all WireOut values
        from the XEM. All wire outs are captured and read at the same time.
        """
        r = _comm(f'UpdateWireOuts'.encode(), self._host)
        return int.from_bytes(r, 'big')

    def WriteToPipeIn(self, epAddr, data):
        """ Writes a block to a Pipe In endpoint.

        Args:
            epAddr (int): The address of the destination Pipe In.
            data (bytearray): Data to be transferred
        """ 
        r = _comm(f'WriteToPipeIn {epAddr} '.encode() + data, self._host)
        return int.from_bytes(r, 'big')

def consume(data, sep=" "):
    action, _, data = data.partition(sep)
    return action

def handle_request(conn):
    global devs
    global xem
    data = conn.recv(1024)
    action = consume(data) 

    if action == b"okCFrontPanelDevices.GetCount":
        count = devices.GetCount()
        conn.send(count.to_bytes(4, "big"))
    elif action == b"okCFrontPanelDevices.GetSerial":
        num = int(consume(data))
        serial = devices.GetSerial(num)
        conn.send(serial.encode())
    elif action == b"okCFrontPanelDevices.Open":
        serialb = consume(data)
        serial = serialb.decode() if serialb != b"None" else None
        xem = devices.Open(serial)
        conn.send(b"")
    elif action == b"okCFrontPanel.Close":
        xem.Close()
        conn.send(b"")
    elif action == b"okCFrontPanel.ConfigureFPGA":
        strFilename = consume(data).decode()
        err = xem.ConfigureFPGA(strFilename)
        conn.send(err.to_bytes(4, "big"))
    elif action == b"okCFrontPanel.GetWireInValue":
        epAddr = int(consume(data))
        val = xem.GetWireInValue(epAddr)
        conn.send(val.to_bytes(4, "big"))
    elif action == b"okCFrontPanel.GetWireOutValue":
        epAddr = int(consume(data))
        val = xem.GetWireOutValue(epAddr)
        conn.send(val.to_bytes(4, "big"))
    elif action == b"okCFrontPanel.IsTriggered":
        epAddr = int(consume(data))
        mask = int(consume(data))
        val = xem.IsTriggered(epAddr, mask)
        conn.send(val.to_bytes(4, "big"))
    elif action == b"okCFrontPanel.SetWireInValue":
        epAddr = int(consume(data))
        val = int(consume(data))
        mask = int(consume(data))
        err = xem.SetWireInValue(epAddr, val, mask)
        conn.send(err.to_bytes(4, "big"))
    elif action == b"okCFrontPanel.UpdateTriggerOuts":
        err = xem.UpdateTriggerOuts()
        conn.send(err.to_bytes(4, "big"))
    elif action == b"okCFrontPanel.UpdateWireIns":
        err = xem.UpdateWireIns()
        conn.send(err.to_bytes(4, "big"))
    elif action == b"okCFrontPanel.UpdateWireOuts":
        err = xem.UpdateWireOuts()
        conn.send(err.to_bytes(4, "big"))
    elif action == b"okCFrontPanel.WriteToPipeIn":
        epAddr = int(consume(data))
        err = xem.SetWireInValue(epAddr, data)
        conn.send(err.to_bytes(4, "big"))

if __name__ == "__main__":
    import logging
    import ok
    import sys
    
    devices = ok.okCFrontPanelDevices()
    xem = None
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
