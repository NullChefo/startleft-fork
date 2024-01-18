from slp_abacus.slp_abacus.parse.abacus_parser import AbacusParser
from slp_abacus.slp_abacus.validate.abacus_mapping_file_validator import AbacusMappingFileValidator
from slp_abacus.slp_abacus.load.abacus_loader import AbacusLoader
from slp_abacus.slp_abacus.map.abacus_mapping_file_loader import AbacusMappingFileLoader
from slp_abacus.slp_abacus.validate.abacus_validator import AbacusValidator
from slp_base.slp_base import MappingLoader, MappingValidator
from slp_base.slp_base import OTMProcessor
from slp_base.slp_base import ProviderValidator
from slp_base.slp_base.provider_loader import ProviderLoader
from slp_base.slp_base.provider_parser import ProviderParser


class AbacusProcessor(OTMProcessor):
    """
    Terraform implementation of OTMProcessor
    """

    def __init__(self, project_id: str, project_name: str, sources: [bytes], mappings: [bytes]):
        self.project_id = project_id
        self.project_name = project_name
        self.mappings = mappings
        self.sources = sources

        self.terraform_loader = None
        self.mapping_loader = None

    def get_provider_validator(self) -> ProviderValidator:
        return AbacusValidator(self.sources)

    def get_provider_loader(self) -> ProviderLoader:
        self.terraform_loader = AbacusLoader(self.sources)
        return self.terraform_loader

    def get_mapping_validator(self) -> MappingValidator:
        return AbacusMappingFileValidator(self.mappings)

    def get_mapping_loader(self) -> MappingLoader:
        self.mapping_loader = AbacusMappingFileLoader(self.mappings)
        return self.mapping_loader

    def get_provider_parser(self) -> ProviderParser:
        return AbacusParser(
                self.project_id,
                self.project_name,
                self.terraform_loader.get_terraform(),
                self.terraform_loader.get_tfgraph(),
                self.mapping_loader.get_mappings())
