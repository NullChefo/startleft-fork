from networkx import DiGraph

from slp_abacus.slp_abacus.objects.abacus_objects import AbacusComponent, AbacusOTM
from slp_abacus.slp_abacus.transformers.hierarchy_calculator import HierarchyCalculator

# CHILD_TYPE: [PARENT_TYPE_1, PARENT_TYPE_2...]
PARENTS_TYPES_BY_CHILDREN_TYPE = {'aws_ecs_task_definition': ['aws_ecs_service']}


class ChildrenCalculator(HierarchyCalculator):

    def __init__(self, otm: AbacusOTM, graph: DiGraph):
        super().__init__(otm, graph.reverse(copy=True))

    def _calculate_component_parents(self, component: AbacusComponent) -> [str]:
        if component.tf_type not in PARENTS_TYPES_BY_CHILDREN_TYPE:
            return []

        return self._find_parent_by_closest_relationship(
            component,
            self._get_parent_candidates(PARENTS_TYPES_BY_CHILDREN_TYPE[component.tf_type]))
