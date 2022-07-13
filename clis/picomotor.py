import tkinter as tk
import socket

class Picomotor(object):
    def __init__(self, name, socket_address, controller_axis, socket_timeout=1.0, socket_buffersize=4096):
        self.name = name
        self.socket_address = socket_address
        self.controller_axis = controller_axis
        self.socket_timeout = socket_timeout
        self.socket_buffersize = socket_buffersize

    def _connect_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.socket_timeout)
        s.connect(self.socket_address)
        response = s.recv(self.socket_buffersize)
        return s
    
    @property
    def position(self):
        s = self._connect_socket()
        try:
            s.send(f'{self.controller_axis}PA?\r'.encode())
            response = s.recv(self.socket_buffersize)
            return int(response)
        finally:
            s.close()

    @position.setter
    def position(self, position):
        s = self._connect_socket()
        try:
            s.send(f'{self.controller_axis}PA{position}\n'.encode())
        finally:
            s.close()


motors = [
#    Picomotor('side probe x', ('192.168.1.55', 23), 3),
#    Picomotor('side probe y', ('192.168.1.55', 23), 4),
    Picomotor('H1 input x', ('192.168.1.12', 23), 3),
    Picomotor('H1 input y', ('192.168.1.12', 23), 4),
    Picomotor('H1 retro x', ('192.168.1.20', 23), 1),
    Picomotor('H1 retro y', ('192.168.1.20', 23), 2),
    Picomotor('H2 input x', ('192.168.1.12', 23), 1),
    Picomotor('H2 input y', ('192.168.1.12', 23), 2),
    Picomotor('H2 retro x', ('192.168.1.20', 23), 3),
    Picomotor('H2 retro y', ('192.168.1.20', 23), 4),
    Picomotor('V  input x', ('192.168.1.22', 23), 1),
    Picomotor('V  input y', ('192.168.1.22', 23), 2),
    ]


window = tk.Tk()
def move_relative(entry, motor, sign):
    def f(event):
        pv = motor.position 
        num_digits = len(f'{pv:+}')
        rindex = num_digits - entry.index(tk.INSERT)
        motor.position = int(pv) + sign * 10**rindex
        entry.delete(0, tk.END)
        entry.insert(0, f'{motor.position:+0{num_digits}}')
        entry.icursor(len(entry.get()) - rindex)
    return f

def move_absolute(entry, motor):
    def f(event):
        motor.position = int(entry.get())
        entry.delete(0, tk.END)
        entry.insert(0, f'{motor.position:+}')
        entry.icursor(len(entry.get()))
    return f

def get_absolute(entry, motor):
    def f(event):
        entry.delete(0, tk.END)
        entry.insert(0, f'{motor.position:+}')
    return f


for motor in motors:
    frame = tk.Frame(window, relief=tk.RAISED, borderwidth=2)
    label = tk.Label(frame, text=motor.name, width=15)
    entry = tk.Entry(frame, width=15, justify=tk.RIGHT)

    frame.pack()
    label.grid(row=0, column=0)
    entry.grid(row=0, column=1)

    entry.insert(0, f'{motor.position:+}')
    
    entry.event_add('<<Increment>>', '<KeyPress-Up>')
    entry.event_add('<<Decrement>>', '<KeyPress-Down>')
    entry.event_add('<<Absolute>>', '<KeyPress-Return>')
    entry.bind('<<Increment>>', move_relative(entry, motor, +1))
    entry.bind('<<Decrement>>', move_relative(entry, motor, -1))
    entry.bind('<<Absolute>>', move_absolute(entry, motor))
    entry.bind('<Button-1>', get_absolute(entry, motor))
    label.bind('<Button-1>', get_absolute(entry, motor))

window.mainloop()
