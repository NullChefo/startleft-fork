from slp_abacus.slp_abacus.matcher.components_and_sgs_matcher import ComponentsAndSGsMatcher
from slp_abacus.slp_abacus.matcher.resource_matcher import ResourcesMatcherContainer
from slp_abacus.slp_abacus.matcher.sg_and_sgrules_matcher import SGAndSGRulesMatcher
from slp_abacus.slp_abacus.matcher.sgs_matcher import SGsMatcher
from slp_abacus.slp_abacus.matcher.strategies.match_strategy import MatchStrategyContainer

MatchStrategyContainer().wire(packages=[__name__])

ResourcesMatcherContainer().wire(modules=[
    ComponentsAndSGsMatcher.__module__,
    SGsMatcher.__module__,
    SGAndSGRulesMatcher.__module__
])
