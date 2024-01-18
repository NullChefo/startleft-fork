from sl_util.sl_util.file_utils import get_byte_data
from slp_abacus.slp_abacus.map.mapping import Mapping
from slp_abacus.slp_abacus.map.abacus_mapping_file_loader import AbacusMappingFileLoader
from slp_abacus.tests.resources.test_resource_paths import terraform_iriusrisk_abacus_aws_mapping

DEFAULT_MAPPING_FILE = get_byte_data(terraform_iriusrisk_abacus_aws_mapping)


class TestAbacusMappingFileLoader:

    def test_resource_load(self):
        # GIVEN a valid TF mapping file
        mapping_file = DEFAULT_MAPPING_FILE

        # WHEN loading the mapping file
        loader = AbacusMappingFileLoader([mapping_file])

        # THEN the mapping file loads correctly
        loader.load()

        # AND a Mappin object is returned
        mapping = loader.get_mappings()
        assert isinstance(mapping, Mapping)
