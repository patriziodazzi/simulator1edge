"""Minimal local fallback for environments without the external simpy dependency."""


class Environment:
    def __init__(self):
        self.now = 0

    def run(self, until=None):
        if until is None:
            return
        self.now = until
