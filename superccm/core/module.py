from typing import Callable, Any, Type
import inspect


class Module:
    """ Module Interface """
    Author: str
    Version: str
    Function: Type

    def __init__(self):
        function = self.__class__.Function
        if inspect.isclass(function):
            function = function()
        if not callable(function):
            raise TypeError('The input object or the instantiated object must be callable.')
        self.function: Callable = function

    def run(self, *args, **kwargs) -> Any:
        return self.function(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    @classmethod
    def desc(cls) -> str:
        content = f'<{cls.__name__}> Author: [{cls.Author}] Version = {cls.Version}'
        if cls.__doc__:
            content += f' Doc: "{cls.__doc__}"'
        return content

    def __repr__(self):
        return self.desc()
