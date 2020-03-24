import asyncio

import sys
import time
import itertools
class Signal:
    go = True
async def spinner(msg):
    flush, write = sys.stdout.flush, sys.stdout.write
    for ch in itertools.cycle('/-|\\|'):
        status = ch + ' ' + msg
        write(status)
        flush()
        write('\x08'*len(status))
        try:
            await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            break
    write('\x08'*len(status))

async def slow_function():
    await asyncio.sleep(3)
    return 42

async def supervisor():
    s = asyncio.ensure_future(spinner('processing'))
    print(s)
    result = await slow_function()
    s.cancel()
    return result

def main():
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(supervisor())
    loop.close()
    print(result)
if __name__ == "__main__":
    main()

