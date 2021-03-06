from uuid import uuid4
from asyncio import Queue


class User:
    id = None
    name = None
    queue = None
    game_id = None

    def __init__(self, name):
        self.id = str(uuid4())
        self.name = name
        self.queue = Queue()
