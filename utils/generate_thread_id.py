import time
import secrets


def generate_thread_id():
    timestamp = int(time.time() * 1000)  # ms
    rand = secrets.token_hex(4)
    thread_id = f"thread-{timestamp}-{rand}"
    return thread_id