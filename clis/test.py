import tkinter as tk
window = tk.Tk()
#button = tk.Button(text='click here')
#button.pack()
#greeting = tk.Label(text='Hey!')
#greeting.pack()

#def handle_keypress(event):
#    print(event.char)
#window.bind("<Key>", handle_keypress)

#e = tk.Entry()
#e.pack()

#def handle_keypress(event):
#    print(event)
#window.bind("<Key>", handle_keypress)

#window.geometry('400x400')
def on_increment(entry):
    def f(event):
        index = entry.index(tk.INSERT)
        inc = + 10**(len(entry.get()) - index)
        nv = int(entry.get()) + inc
        entry.delete(0, tk.END)
        entry.insert(0, nv)
        entry.icursor(index)
    return f

def on_decrement(entry):
    def f(event):
        index = entry.index(tk.INSERT)
        inc = - 10**(len(entry.get()) - index)
        nv = int(entry.get()) + inc
        entry.delete(0, tk.END)
        entry.insert(0, nv)
        entry.icursor(index)
    return f

for i in range(3):
    frame = tk.Frame(window, relief=tk.RAISED, borderwidth=2)
    label = tk.Label(frame, text=f'X{i}', width=15)
    entry = tk.Entry(frame, width=15, justify=tk.RIGHT)

    frame.pack()
    label.grid(row=0, column=0)
    entry.grid(row=0, column=1)

    entry.insert(0, 0)
    
    entry.event_add('<<Increment>>', '<KeyPress-Up>')
    entry.event_add('<<Decrement>>', '<KeyPress-Down>')
    entry.bind('<<Increment>>', on_increment(entry))
    entry.bind('<<Decrement>>', on_decrement(entry))

window.mainloop()
