# <==============================================================>

#    ██████╗ █████╗  ██████╗██╗  ██╗███████╗   ██████╗ ██╗   ██╗
#   ██╔════╝██╔══██╗██╔════╝██║  ██║██╔════╝   ██╔══██╗╚██╗ ██╔╝
#   ██║     ███████║██║     ███████║█████╗     ██████╔╝ ╚████╔╝ 
#   ██║     ██╔══██║██║     ██╔══██║██╔══╝     ██╔═══╝   ╚██╔╝  
#   ╚██████╗██║  ██║╚██████╗██║  ██║███████╗██╗██║        ██║   
#    ╚═════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝        ╚═╝                                                           

# <==============================================================>
#                Module implementing cache objects
# <==============================================================>
#                  @Author: Stefano Bia Carrasco
# <==============================================================>
#  IMPORTS
# <==============================================================>
from typing import Self, Iterator, Any, KeysView, ValuesView, ItemsView
# <==============================================================>
#  CLASSES
# <==============================================================>
class LRUCache[K, V]:
    """
    LRU (Least Recently Used) cache container class
    """
    def __init__(self, size: int) -> None:
        """
        LRUCache object constructor

        :param size: (int) Size of the cache, must be greater than one
        :raises ValueError: When the value of size is invalid
        """
        # Check size
        if (size <= 1):
            raise ValueError('Invalid \'size\' for LRU cache!')
        # Initialize attributes
        # First history element is last discarded cache key
        self.__history: list[K, ...] = [None for _ in range(size+1)] # Preload with None, fixed-size array
        self.__cache: dict[K, V] = {}
        self.__size: int = size

    def __len__(self) -> int:
        """
        Get the length of the cache

        The length of the cache is the number of elements currently stored.

        :returns: (int) The cache length
        """
        return self.__cache.__len__() # Delegates work to dict

    def __contains__(self, key: K) -> bool:
        """
        Check if the cache has a key

        :param key: (K) The key to check for
        :returns: (bool) Whether the cache has an entry for the key or not
        """
        return self.__cache.__contains__(key) # Delegates work to dict

    def __getitem__(self, key: K) -> V:
        """
        Get the corresponding value for a key
        
        :param key: (K) The key to get the value for
        :returns: (V) The key's corresponding value, if any
        :raises KeyError: If the key is not found in the cache
        """
        if (key in self.__cache):
            # Update access history
            self.__update_history(key)
            # Get value for key
            return self.__cache[key]
        # Throw error if key not found
        raise KeyError(f'Key \'{key}\' not found in LRU cache!')

    def __setitem__(self, key: K, value: V) -> None:
        """
        Set the corresponding value for a key
        
        :param key: (K) The key to set the value for, ignores None
        """
        # Ignore None
        if (key != None):
            # Update access history
            self.__update_history(key)
            # Delete first history element, which represents last discarded cache key
            if (self.__history[0] in self.__cache):
                del self.__cache[self.__history[0]]
            # Set value for key
            self.__cache[key] = value

    def __delitem__(self, key: K) -> None:
        """
        Delete the corresponding value for a key

        If the key is not found in the cache the operation fails silently.
        
        :param key: (K) The key to delete the value for
        """
        if (key in self.__cache):
            # Gets the index of key, if this raises an error I should quit programming
            ix = self.__history.index(key)
            # Delete the cache and history entries
            del self.__cache[self.__history[ix]]
            self.__history[ix] = None

    def __eq__(self, other: Self) -> bool:
        """
        Check if two caches are equal

        LRU Caches are considered equal if they
        store the same data and have the same access history.

        :param other: (Self) Other instance to compare to
        :returns: (bool) Whether the two caches are equal
        """
        return (self.__history == other.__history) \
            and (self.__cache == other.__cache)

    def __iter__(self) -> Iterator[K]:
        """
        Get an iterator for the cache

        :returns: (Iterator[K]) The iterator for the cache
        """
        return self.__cache.__iter__() # Delegates work to dict

    def __str__(self) -> str:
        """
        Get a string representation of the cache

        :returns: (str) String representation of the cache
        """
        return f'({self.__size}){self.__history}{self.__cache}'

    @property
    def size(self) -> int:
        """
        Get the size of the cache

        The size of the cache is the maximum number of elements it stores before
        it starts discarding the least recently used ones on new element insertion.

        :returns: (int) The cache size
        """
        return self.__size

    def get(self, key: K, default: V | Any=None) -> V | Any:
        """
        Get the corresponding value for a key

        :param key: (K) The key to get the value for
        :param default: (V | Any) The default value to return if key not in cache
        :returns: (V | Any) The value for the key or the default value in its abscence
        """
        return self.__cache.get(key, default) # Delegates work to dict

    def keys(self) -> KeysView[K]:
        """
        Get the keys of the cache

        :returns: (KeysView[K]) Set-like object providing view of cache's keys
        """
        return self.__cache.keys() # Delegates work to dict

    def values(self) -> ValuesView[V]:
        """
        Get the values of the cache

        :returns: (ValuesView[V]) Set-like object providing view of cache's values
        """
        return self.__cache.values() # Delegates work to dict

    def items(self) -> ItemsView[K, V]:
        """
        Get the items of the cache

        :returns: (ItemsView[K, V]) Set-like object providing view of cache's items
        """
        return self.__cache.items() # Delegates work to dict

    def clear(self) -> None:
        """
        Clear the cache

        Clears the cache and resets its access history.
        """
        # Set all elements of history to None
        for i in range(len(self.__history)):
            self.__history[i] = None
        # Clear cache
        self.__cache.clear() # Delegates work to dict

    def copy(self) -> Self:
        """
        Get a copy of the cache

        :returns: (Self) Copy of the cache as a different instance
        """
        # Create new empty instance
        copy = type(self).__new__(type(self))
        # Initialize attributes with copies
        copy.__history = self.__history.copy()
        copy.__cache = self.__cache.copy()
        copy.__size = self.__size
        return copy

    def __update_history(self, key: K) -> None:
        """
        Update the access history of the cache

        :param key: (K) Key of the access to record
        """
        # Index of the key in history or 0
        ix = self.__history.index(key) \
            if (key in self.__history) else 0
        # Move all elements from history[ix:] one position downwards
        for i,value in enumerate(self.__history[1+ix:], ix):
            self.__history[i] = value
        # After making space, add key to end of history
        self.__history[-1] = key
# <==============================================================>
#  SCRIPT EXECUTION
# <==============================================================>
# If executing as a script
# <==============================================================>
if (__name__ == '__main__'):
    ...
# <==============================================================>