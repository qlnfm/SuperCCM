from abc import ABC


class BaseModule(ABC):
    """ Module abstract class """
    def __init__(self):
        self.name = None
        self.output_name = None

    def __call__(self, *args, **kwargs):
        raise NotImplementedError
