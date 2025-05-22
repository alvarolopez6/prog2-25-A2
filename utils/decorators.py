# <=====================================================================================>

#   ██████╗ ███████╗ ██████╗ ██████╗ ██████╗  █████╗ ████████╗ ██████╗ ██████╗ ███████╗
#   ██╔══██╗██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝
#   ██║  ██║█████╗  ██║     ██║   ██║██████╔╝███████║   ██║   ██║   ██║██████╔╝███████╗
#   ██║  ██║██╔══╝  ██║     ██║   ██║██╔══██╗██╔══██║   ██║   ██║   ██║██╔══██╗╚════██║
#   ██████╔╝███████╗╚██████╗╚██████╔╝██║  ██║██║  ██║   ██║   ╚██████╔╝██║  ██║███████║
#   ╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝

# <=====================================================================================>
#                            Module implementing decorators
# <=====================================================================================>
#                             @Author: Stefano Bia Carrasco
# <=====================================================================================>
#  IMPORTS
# <=====================================================================================>
from typing import Any, Callable, Concatenate
from functools import wraps, update_wrapper
from time import perf_counter as clock
from .cache import LRUCache
# <=====================================================================================>
#  TYPES
# <=====================================================================================>
type AnyCallable = Callable[..., Any]
type Decorator = Callable[[AnyCallable], AnyCallable]
type ParamDecorator[**P] = Callable[Concatenate[AnyCallable, P], AnyCallable]
# <=====================================================================================>
#  DECORATORS
# <=====================================================================================>
def dec_wparams[**P](dec: ParamDecorator[P]) -> Callable[Concatenate[AnyCallable, P], AnyCallable | Decorator]:
    """
    Decorates a decorator
    """
    @wraps(dec) # Mimic wrapped function signature
    def decorator_wrapper(func: AnyCallable=None, *args: P.args, **kwargs: P.kwargs) -> AnyCallable | Decorator:
        # If decorator call
        if func:
            # Return callable
            return dec(func)
        # Parametized decorator
        @wraps(dec) # Mimic wrapped function signature
        def _decorator_wrapper(func: AnyCallable) -> AnyCallable:
            # Return deferred callable
            return dec(func, *args, **kwargs)
        return _decorator_wrapper
    return decorator_wrapper
# <=====================================================================================>
def timed[O, **P](func: Callable[P, O]) -> Callable[P, O]:
    """
    Times a function's calls

    Works as a decorator and returns the passed function
    wrapped in another function that times the function's calls.

    :param func: (Callable[P, O]) Function to time calls for
    :returns: (Callable[P, O]) Wrapped function with timing functionality
    """
    @wraps(func) # Mimic wrapped function signature
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> O:
        # Compute time before and after function call
        st, result, et = clock(), func(*args, **kwargs), clock()
        print(f'<Call {func.__name__}{args}{kwargs} -> took {et - st:.6f} seconds>')
        return result
    return _wrapper
# <=====================================================================================>
@dec_wparams # Decorating a decorator...
def readonly[C](cls: C, attrs: set[str, ...]) -> C:
    """
    Sets a class's instance attributes as readonly

    Works as a decorator and returns the passed class
    with a modified __setattr__ magic function.

    :param cls: (C) Class to manage readonly attributes for
    :param attrs: (tuple[str, ...]) Tuple of attributes to make readonly
    :returns: (C) The modified class object
    """
    # Incorporates private name mangling
    attrs: set[str, ...] = {f'_{cls.__name__}{attr}' if (attr[:2] == '__') else attr for attr in attrs}
    # Magic method function definition
    def _readonly(self, name: str, value: Any) -> None:
        """
        Set the corresponding attribute to value

        Allows changing any attribute except those marked as readonly.

        :param name: (str) Name of the attribute to set
        :param value: (Any) Value to set the attribute to
        :raises ValueError: When trying to change readonly attributes
        """
        # If readonly attribute and already set
        if (name in attrs) and (name in self.__dict__) and (self.__dict__[name] != None):
            raise ValueError(f'Cannot change readonly attribute {type(self).__name__}.{name}!')
        # Else work properly
        self.__dict__[name] = value
    # Assing function to magic method
    cls.__setattr__ = _readonly
    # Return class
    return cls
# <=====================================================================================>
@dec_wparams # Decorating a decorator...
class memoize[O, **P]:
    """
    Memoization decorator class

    Transforms the functions it decorates into memoized functions.
    """
    def __init__(self, func: Callable[P, O], xparams: tuple[str, ...]=(), size: int=8) -> None:
        """
        Memoize object constructor

        :param func: (Callable[P, O]) Function to memoize
        :param xparams: (tuple[str, ...]) Tuple containing function's parameter names of arguments to use for result indexing, default is () which uses all params
        :param size: (int) Size of the memoization cache, must be greater than one, default is 8
        :raises ValueError: When the value of size is invalid
        """
        # Mimic wrapped function signature
        update_wrapper(self, func)
        # Memoized function
        self.__func: Callable[P, O] = func
        # Memoization cache
        self.__cache: LRUCache[str, O] = LRUCache(size) # Throws error if size <= 1
        # Dict with indexing parameter names as keys and parameter positions as values
        self.__map: dict[str, int] = {
            v:i
            for i,v in enumerate(func.__code__.co_varnames[:func.__code__.co_argcount]) # Get name of func's parameters
            if (v in xparams) or (len(xparams) == 0) # If in indexing param list
        }

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> O:
        """
        Wraps the memoized function by implementing the functionality for when calling on an instance

        Gets the cached result for the provided parameters, if previously cached, or computes and caches the result.

        :param args: (P.args) Variadic positional arguments
        :param kwargs: (P.kwargs) Variadic keyword arguments
        :returns: (O) Memoized function result
        """
        # Compute function call key
        key = self.__get_indexkey(*args, **kwargs)
        # If not in cache
        if not (key in self.__cache):
            # Save it to cache and return it
            self.__cache[key] = self.__func(*args, **kwargs)
        # Else return it from cache
        return self.__cache[key]

    def __get_indexkey(self, *args: P.args, **kwargs: P.kwargs) -> str:
        """
        Get the indexing key for a set of arguments

        :param args: (P.args) Variadic positional arguments
        :param kwargs: (P.kwargs) Variadic keyword arguments
        :returns: (str) The indexing key for the set of arguments
        """
        skey = ['/']
        # Loop trough mapped args
        for i in self.__map.values(): # Loop trough this as it has static order
            # If mapped parameter is an argument
            if (i < len(args)):
                skey.append(f'{args[i]}/')
        # Loop trough mapped kwargs
        for k in self.__map.keys(): # Loop trough this as it has static order
            # If mapped parameter is an argument
            if (k in kwargs):
                skey.append(f'{kwargs[k]}/')
        # Join and return
        return ''.join(skey)
# <=====================================================================================>
#  SCRIPT EXECUTION
# <=====================================================================================>
# If executing as a script
# <=====================================================================================>
if (__name__ == '__main__'):
    ...
# <=====================================================================================>