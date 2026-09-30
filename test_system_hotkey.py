import time
from system_hotkey import SystemHotkey
hk = SystemHotkey()
def callback(event, *args):
    print(f"Hotkey pressed: {event}")
hk.register(('control', 'option', 'space'), callback=callback)
print("Listening for Ctrl+Option+Space... (5 sec)")
time.sleep(5)
print("Done.")
