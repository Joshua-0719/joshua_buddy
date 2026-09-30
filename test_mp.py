import multiprocessing as mp
import time
from pynput import keyboard

def worker(q):
    def on_press(key):
        print(f"worker saw: {key}")
        q.put(str(key))
        if key == keyboard.Key.esc:
            return False
    with keyboard.Listener(on_press=on_press) as l:
        l.join()

if __name__ == '__main__':
    q = mp.Queue()
    p = mp.Process(target=worker, args=(q,))
    p.start()
    print("Process started. Press keys (Esc to quit)...")
    while True:
        try:
            val = q.get(timeout=1)
            print(f"Main got: {val}")
            if val == "Key.esc":
                break
        except:
            if not p.is_alive():
                break
    p.join()
