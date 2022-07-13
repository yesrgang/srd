from labd.libs._serial import SerialProxy

#visa = VisaProxy(('192.168.1.49', 42922))
serial = SerialProxy(('192.168.107.58', 42922))
message = serial._echo('hello!')
print(message)
ser = serial.Serial('COM3')
ser.write(b'0in\r\n')
ans = ser.read_until()
print(ans)
ser.write(b'0fw\r\n')

