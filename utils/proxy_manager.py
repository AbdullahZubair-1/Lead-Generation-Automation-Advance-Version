import random

PROXIES = []

def get_proxy():
    if PROXIES:
        return random.choice(PROXIES)
    return None 