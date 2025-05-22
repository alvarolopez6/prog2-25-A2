from typing import Self

class Singleton[C: object](type):
    """
    Singleton metaclass

    Enforces the singleton pattern on a class.
    """
    __instances: dict[Self, C] = {}

    def __call__[**P](cls, *args: P.args, **kwargs: P.kwargs) -> C:
        """
        Construct a class object following the singleton pattern

        Constructs an object or returns one if it was already made before.
        """
        if not (cls in cls.__instances):
            cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]