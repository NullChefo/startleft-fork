from typing import List, Dict, Union

import pygraphviz
from networkx import nx_agraph, DiGraph

from sl_util.sl_util.file_utils import read_byte_data
from sl_util.sl_util.json_utils import yaml_reader
from slp_base import ProviderLoader, LoadingIacFileError
from slp_abacus.slp_abacus.load.abacus_to_resource_dict import AbacusToResourceDict


def load_abacus(source: bytes) -> Dict:
    try:
        return yaml_reader(source)
    except Exception:
        pass


def generate_invalid_iac_files_error() -> LoadingIacFileError:
    return LoadingIacFileError(
        title='IaC files are not valid',
        message='The provided IaC files could not be processed'
    )


def generate_wrong_number_of_sources_error() -> LoadingIacFileError:
    return LoadingIacFileError(
        title='Wrong number of files',
        message='Required one abacus and one tfgraph files'
    )


class abacusLoader(ProviderLoader):

    def __init__(self, sources: List[bytes]):
        self.sources = sources
        self.abacus: Union[Dict, None] = None

    def load(self):
        self.__load_sources()
        if self.abacus:
            self.__map_abacus_to_resources()
            self.__map_abacus_to_variables()

    def __load_sources(self):
        if len(self.sources) != 2:
            raise generate_wrong_number_of_sources_error()

        for source in self.sources:
            if self.abacus is None:
                self.abacus = load_abacus(source)
                if self.abacus is not None:
                    continue

    def __get_abacus_resources(self) -> Dict:
        return self.abacus \
            .get('configuration', {}) \
            .get('root_module', {}) \
            .get('resources', {})

    def __get_abacus_root_module(self) -> List[Dict]:
        return [self.abacus['planned_values']['root_module']]

    def __get_abacus_variables(self) -> Dict:
        return self.abacus.get('variables', {})
