from networkx import DiGraph

from slp_abacus.slp_abacus.objects.abacus_objects import AbacusComponent, AbacusOTM
from slp_abacus.slp_abacus.transformers.hierarchy_calculator import HierarchyCalculator

PARENT_TYPES = ['aws_subnet', 'aws_vpc', 'azurerm_subnet', 'azurerm_virtual_network']


class ParentCalculator(HierarchyCalculator):

    def __init__(self, otm: AbacusOTM, graph: DiGraph):
        super().__init__(otm, graph)
        self.parent_candidates = self._get_parent_candidates(PARENT_TYPES)

    def _calculate_component_parents(self, component: AbacusComponent) -> [str]:
        return self._find_parent_by_closest_relationship(component, self.parent_candidates)


