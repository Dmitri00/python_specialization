import asyncio
import aiohttp
import os.path
COUNTRY_CODES = 'CN IN US ID BR PK NG BD RU JP \
    MX PH VN ET EG DE IR TR CD FR'.split()
BASE_URL = 'http://fluppy.org/data/flags'
DEST_DIR = 'downloads/'

def saveflag(flag, code):
    path = os.path.join(DEST_DIR, code)
    with open(path, 'wb') as f:
        f.write(flag)
def show(code):
    print(code)
async def get_flag(code):
    url = '{}/{cc}/{cc}.gif'.format(BASE_URL, cc=code.lower())
    async with aiohttp.request('GET', url) as result:
        image = result.read()
    return image
async def download_one(code):
    flag = await get_flag(code)
    show(code)
    saveflag(flag, code+ '.gif')
def download_many(cc_list):
    loop = asyncio.get_event_loop()
    tasks = [download_one(cc) for cc in cc_list]
    wait_coro = asyncio.wait(tasks)
    res, _ = loop.run_until_complete(wait_coro)
    loop.close()
    print(res)
    return
if __name__ == "__main__":
    download_many(COUNTRY_CODES)


    