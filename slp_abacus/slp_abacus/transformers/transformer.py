import abc

from networkx import DiGraph

from slp_abacus.slp_abacus.objects.abacus_objects import AbacusOTM


class Transformer(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'transform') and callable(subclass.transform)) or NotImplemented

    def __init__(self, otm: AbacusOTM, graph: DiGraph = None):
        self.otm: AbacusOTM = otm
        self.graph: DiGraph = graph

    @abc.abstractmethod
    def transform(self):
        """ perform the necessary operations to transform and enrich the OTM """
        raise NotImplementedError
