from langgraph.checkpoint.redis import RedisSaver


def get_checkpointer():
    REDIS_URI = "redis://localhost:6379"
    checkpointer = None
    with RedisSaver.from_conn_string(REDIS_URI) as _checkpointer:
        _checkpointer.setup()
        checkpointer = _checkpointer

    return checkpointer

