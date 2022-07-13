from labd.libs._visa import VisaProxy

#visa = VisaProxy(('192.168.1.49', 42922))
visa = VisaProxy(('192.168.107.58', 42922))
message = visa._echo('hello!')
rm = visa.ResourceManager()
print(rm.list_resources())

#inst = rm.open_resource("GPIB0::2::INSTR")
#print(inst.query("*IDN?"))
#inst.timeout = 1000
#print(inst.timeout)
#print(inst.write("*IDN?"))
#print(inst.read())
