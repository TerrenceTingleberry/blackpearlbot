import asyncio
import logging

from .database import SESSION

try:
    loop = asyncio.get_running_loop()
except RuntimeError:  # 'RuntimeError: There is no current event loop...'
    loop = None

if loop and loop.is_running():
    loop.create_task(SESSION.create_all())
else:
    logging.debug("Starting new event loop")
    result = asyncio.run(SESSION.create_all())
