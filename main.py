import asyncio
import hashlib
import os
import tempfile

import aiohttp


async def get_files_paths(url=None):

    """File paths are recursively collected here"""
    if not url:
        url = 'https://gitea.radium.group/api/v1/repos' \
            '/radium/project-configuration/contents'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=False) as response:
            contents = await response.json()
            files = []
            for item in contents:
                if item['type'] == 'file':
                    files.append(item['download_url'])
                elif item['type'] == 'dir':
                    subdir_files = await get_files_paths(item['url'])
                    files.extend(subdir_files)
            return files


async def download_and_hash(url: str, path: str):

    """Download and hashing is implemented """

    async with aiohttp.ClientSession() as session:
        async with session.head(url, ssl=False) as response:
            content = await response.read()
            sha256 = hashlib.sha256(content).hexdigest()
            filename = os.path.basename(url)
            filepath = os.path.join(path, filename)
            with open(filepath, 'wb') as f:
                f.write(content)
            return filepath, sha256


async def main():

    """Function for main process of downloading files
    to the temporary directory """

    urls = await get_files_paths()

    tasks = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for url in urls:
            task = asyncio.create_task(download_and_hash(url, tmpdir))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        for filepath, sha256 in results:
            print(f"File {filepath} downloaded with sha256: {sha256}")

asyncio.run(main())
