from typing import Union

from slp_abacus.slp_abacus.objects.abacus_objects import AbacusOTM

LAUNCH_TEMPLATE_TYPES = ['aws_launch_template']


def _extract_value(value: {}) -> Union[list, str]:
    return isinstance(value, dict) and value.get('value', None)


class VariablesLoader:

    def __init__(self, otm: AbacusOTM, abacus: {}):
        self.otm = otm
        self.variables = abacus.get('variables', {})

    def load(self):
        for k, v in self.variables.items():
            value = _extract_value(v)
            if value:
                self.otm.variables[k] = value
