from abc import ABC, abstractmethod
from .module import Module
import inspect


class WorkFlow(ABC):
    """ WorkFlow Interface """
    Author: str
    Version: str

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    @classmethod
    def desc(cls) -> str:
        content = f'<{cls.__name__}> Author: [{cls.Author}] Version = {cls.Version}'
        if cls.__doc__:
            content += f' Doc: "{cls.__doc__}"'
        return content

    def __repr__(self):
        desc = self.desc()
        cls = self.__class__
        modules = [item for item in cls.__dict__.values()
                   if inspect.isclass(item) and issubclass(item, Module)]
        for module in modules:
            desc += f'\n - {module.desc()}'
        return desc
