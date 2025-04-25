import os

import aiofiles
import logging
import tempfile
from typing import Union
from fastapi import BackgroundTasks, UploadFile, HTTPException

logger = logging.getLogger("backend.utils.utils")

CHUNK_SIZE = 1024 * 1024  # adjust the chunk size as desired

async def get_fastapi_file_locally(
        background_tasks: BackgroundTasks | None,
        file_data: UploadFile,
        extension: Union[None, str] = None
) -> Union[tuple[int, str, str], Exception]:
    """
    Caches a file locally - used for reading moderately sized files efficiently.

    :param background_tasks: Create a background task to delete the temporary file after a value is returned.
    :param file_data: The file to cache.
    :param extension: Extension for the filename. Use "" if no extension. Default (None) will attempt to infer the extension automatically.
    :return: Tuple containing a file descriptor, path and extension, or an exception if an error occurred.
    """
    logger.debug("Get locally start")
    file_name = file_data.filename
    if extension is None:
        if "." in file_name:
            extension = "." + file_name.split('.')[-1]
    elif extension == "":
        extension = None
    try:
        fd, path = tempfile.mkstemp(suffix=extension)
        async with aiofiles.open(path, 'wb') as f:
            while chunk := await file_data.read(CHUNK_SIZE):
                await f.write(chunk)
        if background_tasks is not None:
            background_tasks.add_task(close_and_remove_file(fd, path))
        return fd, path, extension
    except Exception as e:
        return e


def close_and_remove_file(fd: int, path: str):
    def localClose():
        # os.close(fd)
        os.remove(path)

    return localClose


async def cache_multi_segy(upload_files, background_tasks: BackgroundTasks):
    temp_file_paths = []
    for file in upload_files:
        logger.debug("before_get_locally")
        local_result = await get_fastapi_file_locally(background_tasks=background_tasks, file_data=file,
                                                      extension=".sgy")
        logger.debug("local_result:", local_result)
        if local_result is Exception:
            raise HTTPException(status_code=500, detail=f"Error processing file {file.filename}.")
        file_descriptor, file_path, extension = local_result
        temp_file_paths.append(file_path)
    return temp_file_paths
