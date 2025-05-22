from file_utils import Path

class CorruptedFile(Exception):
    def __init__(self, path: str | Path, msg: str) -> None:
        self.path = path
        self.msg = msg

    def __str__(self):
        return f'CorruptedFile ({self.path}): {self.msg}'