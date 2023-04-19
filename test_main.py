import hashlib
import os
import tempfile

import aiohttp
import pytest

from main import download_and_hash, get_files_paths


@pytest.mark.asyncio
async def test_if_file_paths_are_strs():
    files = await get_files_paths()
    for file in files:
        assert type(file) == str


@pytest.mark.asyncio
async def test_if_filepath_and_sha256_are_created():
    url = 'https://example.com/test.txt'
    async with aiohttp.ClientSession() as session:
        async with session.head(url, ssl=False) as response:
            content = await response.read()
            with tempfile.TemporaryDirectory() as tempdir:
                path = tempdir
                filepath, sha256 = await download_and_hash(url, path)
                # Check that the file was downloaded to the expected path
                assert os.path.exists(filepath)
                # Check that the file's SHA256 hash matches the expected value
                assert sha256 == hashlib.sha256(content).hexdigest()
