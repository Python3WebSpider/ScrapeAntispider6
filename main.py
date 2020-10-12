import asyncio
import aiohttp
from pyquery import PyQuery as pq
from loguru import logger

MAX_ID = 100
CONCURRENCY = 5
TARGET_URL = 'https://antispider6.scrape.center'
ACCOUTPOOL_URL = 'http://localhost:6789/antispider6/random'

semaphore = asyncio.Semaphore(CONCURRENCY)


async def parse_detail(html):
    doc = pq(html)
    title = doc('.item h2').text()
    categories = [item.text() for item in doc('.item .categories span').items()]
    cover = doc('.item .cover').attr('src')
    score = doc('.item .score').text()
    drama = doc('.item .drama').text().strip()
    return {
        'title': title,
        'categories': categories,
        'cover': cover,
        'score': score,
        'drama': drama
    }


async def fetch_credential(session):
    async with session.get(ACCOUTPOOL_URL) as response:
        return await response.text()


async def scrape_detail(session, url):
    async with semaphore:
        credential = await fetch_credential(session)
        headers = {'cookie': credential}
        logger.debug(f'scrape {url} using credential {credential}')
        async with session.get(url, headers=headers) as response:
            html = await response.text()
            data = await parse_detail(html)
            logger.debug(f'data {data}')


async def main():
    session = aiohttp.ClientSession()
    tasks = []
    for i in range(1, MAX_ID + 1):
        url = f'{TARGET_URL}/detail/{i}'
        task = asyncio.ensure_future(scrape_detail(session, url))
        tasks.append(task)
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
