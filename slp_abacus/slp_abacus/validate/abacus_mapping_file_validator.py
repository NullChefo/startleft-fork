from slp_base.slp_base import MultipleMappingFileValidator
from slp_base.slp_base.schema import Schema


class AbacusMappingFileValidator(MultipleMappingFileValidator):
    schema_filename = 'iac_abacus_mapping_schema.json'

    def __init__(self, mapping_files: [bytes]):
        super(AbacusMappingFileValidator, self).__init__(
            Schema.from_package('slp_abacus', self.schema_filename), mapping_files)
