from utils.db_store import store


async def get_persona():
    return store.db
