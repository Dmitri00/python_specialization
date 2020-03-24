import threading
import sys
import time
import itertools
class Signal:
    go = True
def spinner(msg, signal):
    flush, write = sys.stdout.flush, sys.stdout.write
    for ch in itertools.cycle('/-|\\'):
        status = ch + ' ' + msg
        write(status)
        flush()
        write('\x08'*len(status))
        time.sleep(0.1)
        if not signal.go:
            break
    write(' '*len(status) + '\x08'*len(status))
        
def slow_function():
    time.sleep(3)
    return 42

def supervisor():
    signal = Signal()
    t = threading.Thread(target=spinner, args=['processing', signal])
    print(t)
    t.start()
    result = slow_function()
    signal.go = False
    t.join()
    return result

def main():
    print(supervisor())
if __name__ == "__main__":
    main()
