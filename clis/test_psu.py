from srd.devs import test_psu

dev = test_psu.DeviceProxy(('192.168.1.91', 42922))

def get_output(event=None):
    if dev.output:
        output_button.config(text='ON')
    else: 
        output_button.config(text='OFF')

def change_output(event):
    prev_disp = output_button.config('text')[-1]
    prev_resp = dev.output
    if (prev_disp == 'OFF') and (prev_resp == False):
        dev.output = True
        output_button.config(text='ON')
    if (prev_disp == 'ON') and (prev_resp == True):
        dev.output = False
        output_button.config(text='OFF')
    else:
        get_output(event)
        

def move_voltage_relative(sign):
    def f(event):
        prev_disp = float(voltage_entry.get())
        prev_resp = dev.voltage_setpoint
        if f'{prev_disp:+.2f}' == f'{prev_resp:+.2f}':
            num_digits = len(f'{prev_resp:+.2f}')
            rindex = num_digits - voltage_entry.index(tk.INSERT)
            dindex = len(f'{prev_resp:+.2f}'.split('.')[-1])
            sindex = rindex - dindex
            sindex -= 1 if sindex > 0 else 0
            dev.voltage_setpoint = prev_disp + sign * 10**(sindex)
            voltage_entry.delete(0, tk.END)
            voltage_entry.insert(0, f'{dev.voltage_setpoint:+.2f}')
            voltage_entry.icursor(len(voltage_entry.get()) - rindex)
        else:
            print('oops')
            voltage_entry.delete(0, tk.END)
            voltage_entry.insert(0, f"{dev.voltage_setpoint:+.2f}")
    return f

def move_voltage_absolute(event):
    dev.voltage_setpoint = float(voltage_entry.get())
    voltage_entry.delete(0, tk.END)
    voltage_entry.insert(0, f'{dev.voltage_setpoint:+.2f}')
    voltage_entry.icursor(len(voltage_entry.get()))

def get_voltage(event=None):
    voltage_entry.delete(0, tk.END)
    voltage_entry.insert(0, f'{dev.voltage_setpoint:+.2f}')

def move_current_relative(sign):
    def f(event):
        prev_disp = float(current_entry.get())
        prev_resp = dev.current_setpoint
        if f'{prev_disp:+.2f}' == f'{prev_resp:+.2f}':
            num_digits = len(f'{prev_resp:+.2f}')
            rindex = num_digits - current_entry.index(tk.INSERT)
            dindex = len(f'{prev_resp:+.2f}'.split('.')[-1])
            sindex = rindex - dindex
            sindex -= 1 if sindex > 0 else 0
            dev.current_setpoint = prev_disp + sign * 10**(sindex)
            current_entry.delete(0, tk.END)
            current_entry.insert(0, f'{dev.current_setpoint:+.2f}')
            current_entry.icursor(len(current_entry.get()) - rindex)
        else:
            print('oops')
            current_entry.delete(0, tk.END)
            current_entry.insert(0, f"{dev.current_setpoint:+.2f}")
    return f


def move_current_absolute(event):
    dev.current_setpoint = float(current_entry.get())
    current_entry.delete(0, tk.END)
    current_entry.insert(0, f'{dev.current_setpoint:+.2f}')
    current_entry.icursor(len(current_entry.get()))

def get_current(event=None):
    current_entry.delete(0, tk.END)
    current_entry.insert(0, f'{dev.current_setpoint:+.2f}')


import tkinter as tk
window = tk.Tk()
frame = tk.Frame(window, relief=tk.RAISED, borderwidth=2)
output_label = tk.Label(frame, text='Test PSU', width=15)
output_button = tk.Button(frame, width=15)
voltage_label = tk.Label(frame, text='Voltage (V)', width=15)
voltage_entry = tk.Entry(frame, width=15, justify=tk.RIGHT)
current_label = tk.Label(frame, text='Current (A)', width=15)
current_entry = tk.Entry(frame, width=15, justify=tk.RIGHT)
frame.pack()

output_label.grid(row=0, column=0)
output_button.grid(row=0, column=1)
voltage_label.grid(row=1, column=0)
voltage_entry.grid(row=1, column=1)
current_label.grid(row=2, column=0)
current_entry.grid(row=2, column=1)

output_label.bind('<Button-1>', get_output)
output_button.bind('<Button-1>', change_output)

voltage_entry.event_add('<<Increment>>', '<KeyPress-Up>')
voltage_entry.event_add('<<Decrement>>', '<KeyPress-Down>')
voltage_entry.event_add('<<Absolute>>', '<KeyPress-Return>')
voltage_entry.bind('<<Increment>>', move_voltage_relative(+1))
voltage_entry.bind('<<Decrement>>', move_voltage_relative(-1))
voltage_entry.bind('<<Absolute>>', move_voltage_absolute)
voltage_entry.bind('<Button-1>', get_voltage)

current_entry.event_add('<<Increment>>', '<KeyPress-Up>')
current_entry.event_add('<<Decrement>>', '<KeyPress-Down>')
current_entry.event_add('<<Absolute>>', '<KeyPress-Return>')
current_entry.bind('<<Increment>>', move_current_relative(+1))
current_entry.bind('<<Decrement>>', move_current_relative(-1))
current_entry.bind('<<Absolute>>', move_current_absolute)
current_entry.bind('<Button-1>', get_current)

get_output()
get_voltage()
get_current()

window.mainloop()
