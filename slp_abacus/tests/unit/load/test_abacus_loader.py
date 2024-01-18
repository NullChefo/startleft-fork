import random
from copy import deepcopy
from json import JSONDecodeError
from typing import List
from unittest.mock import patch, Mock

from networkx import DiGraph
from pytest import raises, mark, param, fixture

from sl_util.sl_util.str_utils import get_bytes
from slp_base import LoadingIacFileError
from slp_abacus.slp_abacus.load.abacus_loader import AbacusLoader
from slp_abacus.tests.resources import test_resource_paths
from slp_abacus.tests.util.asserts import assert_resource_values
from slp_abacus.tests.util.builders import build_abacus, generate_resources, generate_child_modules

INVALID_YAML = test_resource_paths.invalid_yaml
TF_FILE_YAML_EXCEPTION = JSONDecodeError('HLC2 cannot be processed as JSON', doc='sample-doc', pos=0)


@fixture
def mock_load_abacus(mocker, mocked_abacus):
    mocker.patch('yaml.load', side_effect=mocked_abacus)


@fixture(autouse=True)
def mocked_graph():
    yield Mock()


@fixture(autouse=True)
def mock_load_graph(mocker, mocked_graph):
    mocker.patch('slp_abacus.slp_abacus.load.abacus_loader.load_tfgraph', side_effect=mocked_graph)


class TestAbacusLoader:

    @patch('slp_abacus.slp_abacus.load.abacus_loader.load_tfgraph')
    @patch('yaml.load')
    def test_load_abacus_and_graph(self, yaml_mock, from_agraph_mock):
        # GIVEN a valid plain Terraform Plan file with no modules
        yaml_mock.side_effect = [build_abacus(resources=generate_resources(2))]

        # AND a mocked graph load result
        graph_label = 'Mocked Graph'
        from_agraph_mock.side_effect = [DiGraph(label=graph_label)]

        # WHEN AbacusLoader::load is invoked
        abacus_loader = AbacusLoader(sources=[b'MOCKED', b'MOCKED'])
        abacus_loader.load()

        # THEN the ABACUS is loaded
        assert abacus_loader.get_terraform() is not None

        # AND the TFGRAPH is also loaded
        assert abacus_loader.get_tfgraph().graph['label'] == graph_label

    @patch('yaml.load')
    def test_load_no_modules(self, yaml_mock):
        # GIVEN a valid plain Terraform Plan file with no modules
        yaml_mock.side_effect = [build_abacus(resources=generate_resources(2))]

        # WHEN AbacusLoader::load is invoked
        abacus_loader = AbacusLoader(sources=[b'MOCKED', b'MOCKED'])
        abacus_loader.load()

        # THEN TF contents are loaded in AbacusLoader.terraform
        assert abacus_loader.terraform
        resources = abacus_loader.terraform['resource']
        assert len(resources) == 2

        # AND resource_id, resource_type, resource_name and resource_properties are right

        for i, resource in enumerate(resources):
            i += 1
            assert resource['resource_id'] == f'r{i}-addr'
            assert resource['resource_type'] == f'r{i}-type'
            assert resource['resource_name'] == f'r{i}-name'

            assert_resource_values(resource['resource_values'])

    @patch('yaml.load')
    def test_load_only_modules(self, yaml_mock):
        # GIVEN a valid plain Terraform Plan file with only modules
        yaml_mock.side_effect = [build_abacus(
            child_modules=generate_child_modules(module_count=2, resource_count=2))]

        # WHEN AbacusLoader::load is invoked
        abacus_loader = AbacusLoader(sources=[b'MOCKED', b'MOCKED'])
        abacus_loader.load()

        # THEN TF contents are loaded in AbacusLoader.terraform
        assert abacus_loader.terraform
        resources = abacus_loader.terraform['resource']
        assert len(resources) == 4

        # AND resource_id, resource_type, resource_name and resource_properties are right
        resource_index = 0
        for module_index in range(1, 3):
            module_address = f'cm{module_index}-addr'

            for child_index in range(1, 3):
                resource = resources[resource_index]

                assert resource['resource_id'] == f'r{child_index}-addr'
                assert resource['resource_type'] == f'r{child_index}-type'
                assert resource['resource_name'] == f'{module_address}.r{child_index}-name'

                assert_resource_values(resource['resource_values'])

                resource_index += 1

    @patch('yaml.load')
    def test_load_nested_modules(self, yaml_mock):
        # GIVEN a valid plain Terraform Plan file with nested modules
        yaml_mock.side_effect = [build_abacus(
            child_modules=generate_child_modules(
                module_count=1,
                child_modules=generate_child_modules(module_count=1, resource_count=1)))]

        # WHEN AbacusLoader::load is invoked
        abacus_loader = AbacusLoader(sources=[b'MOCKED', b'MOCKED'])
        abacus_loader.load()

        # THEN TF contents are loaded in AbacusLoader.terraform
        assert abacus_loader.terraform
        resources = abacus_loader.terraform['resource']
        resource = resources[0]

        # AND resource_id, resource_type, resource_name and resource_properties are right
        assert len(resources) == 1

        assert resource['resource_id'] == 'r1-addr'
        assert resource['resource_type'] == 'r1-type'
        assert resource['resource_name'] == 'cm1-addr.cm1-addr.r1-name'

        assert_resource_values(resource['resource_values'])

    @patch('yaml.load')
    def test_load_complex_structure(self, yaml_mock):
        # GIVEN a valid plain Terraform Plan file with modules and root-level resources
        yaml_mock.side_effect = [build_abacus(
            resources=generate_resources(1),
            child_modules=generate_child_modules(module_count=1, resource_count=1))]

        # WHEN AbacusLoader::load is invoked
        abacus_loader = AbacusLoader(sources=[b'MOCKED', b'MOCKED'])
        abacus_loader.load()

        # THEN TF contents are loaded in AbacusLoader.terraform
        assert abacus_loader.terraform
        resources = abacus_loader.terraform['resource']
        assert len(resources) == 2

        # AND resource_type, resource_name and resource_properties from top level are right
        resource = resources[0]

        assert resource['resource_id'] == 'r1-addr'
        assert resource['resource_type'] == 'r1-type'
        assert resource['resource_name'] == 'r1-name'

        assert_resource_values(resource['resource_values'])

        # AND resource_type, resource_name and resource_properties from child modules are right
        resource = resources[1]
        assert resource['resource_id'] == 'r1-addr'
        assert resource['resource_type'] == 'r1-type'
        assert resource['resource_name'] == 'cm1-addr.r1-name'

        assert_resource_values(resource['resource_values'])

    @patch('yaml.load')
    def test_load_resources_same_name(self, yaml_mock):
        # GIVEN a valid plain Terraform Plan file with only one module
        abacus = build_abacus(
            child_modules=generate_child_modules(module_count=1, resource_count=1))

        # AND two resources with the same name
        abacus_resources = abacus['planned_values']['root_module']['child_modules'][0]['resources']
        duplicated_resource = deepcopy(abacus_resources[0])
        duplicated_resource['index'] = 1
        abacus_resources.append(duplicated_resource)

        yaml_mock.side_effect = [abacus]

        # WHEN AbacusLoader::load is invoked
        abacus_loader = AbacusLoader(sources=[b'MOCKED', b'MOCKED'])
        abacus_loader.load()

        # THEN TF contents are loaded in AbacusLoader.terraform
        assert abacus_loader.terraform
        resources = abacus_loader.terraform['resource']
        assert len(resources) == 1

        # AND The duplicated resource is unified and the index is no present in name or id
        assert resources[0]['resource_id'] == 'r1-addr'
        assert resources[0]['resource_name'] == 'cm1-addr.r1-name'

    @patch('yaml.load')
    def test_load_modules_same_name(self, yaml_mock):
        # GIVEN a valid plain Terraform Plan file with only one module
        abacus = build_abacus(
            child_modules=generate_child_modules(module_count=1, resource_count=1))

        # AND two resources with the same name
        abacus_modules = abacus['planned_values']['root_module']['child_modules']

        original_module = abacus_modules[0]
        duplicated_module = deepcopy(abacus_modules[0])

        original_module['address'] = f'{original_module["address"]}["zero"]'
        original_module['resources'][0][
            'address'] = f'{original_module["address"]}.{original_module["resources"][0]["address"]}'

        duplicated_module['address'] = f'{duplicated_module["address"]}["one"]'
        duplicated_module['resources'][0][
            'address'] = f'{duplicated_module["address"]}.{duplicated_module["resources"][0]["address"]}'

        abacus_modules.append(duplicated_module)

        yaml_mock.side_effect = [abacus]

        # WHEN AbacusLoader::load is invoked
        abacus_loader = AbacusLoader(sources=[b'MOCKED', b'MOCKED'])
        abacus_loader.load()

        # THEN TF contents are loaded in AbacusLoader.terraform
        assert abacus_loader.terraform
        resources = abacus_loader.terraform['resource']
        assert len(resources) == 1

        # AND The duplicated resource is unified and the index is not present in name or id
        assert resources[0]['resource_id'] == 'cm1-addr.r1-addr'
        assert resources[0]['resource_name'] == 'cm1-addr.r1-name'

    @patch('yaml.load')
    def test_load_no_resources(self, yaml_mock):
        # GIVEN a valid Terraform Plan file with no resources
        yaml_mock.side_effect = [{'planned_values': {'root_module': {}}}]

        # WHEN AbacusLoader::load is invoked
        abacus_loader = AbacusLoader(sources=[b'MOCKED', b'MOCKED'])
        abacus_loader.load()

        # THEN AbacusLoader.terraform is an empty dictionary
        assert abacus_loader.terraform == {}

    @patch('yaml.load')
    def test_load_empty_abacus(self, yaml_mock):
        # GIVEN an empty ABACUS
        yaml_mock.side_effect = [{}]

        # WHEN AbacusLoader::load is invoked
        abacus_loader = AbacusLoader(sources=[b'MOCKED', b'MOCKED'])
        abacus_loader.load()

        # THEN AbacusLoader.terraform is an empty dictionary
        assert abacus_loader.terraform == {}

    @mark.parametrize('sources', [
        param([], id='no sources'),
        param([b'MOCKED'], id='one source'),
        param([b'MOCKED'] * random.randint(3, 10), id='more than two sources')
    ])
    def test_load_invalid_number_of_sources(self, sources: List[bytes]):
        # GIVEN an invalid number of sources

        # WHEN AbacusLoader::load is invoked
        # THEN a LoadingIacFileError is raised
        with raises(LoadingIacFileError) as error:
            AbacusLoader(sources=sources).load()

        # AND an empty IaC file message is on the exception
        assert error.value.title == 'Wrong number of files'
        assert error.value.message == 'Required one abacus and one tfgraph files'

    @mark.usefixtures('mock_load_abacus')
    @mark.parametrize('mocked_abacus,mocked_graph', [
        param([None], [None], id='no valid sources'),
        param([None, None], [Mock()], id='no abacus'),
        param([Mock()], [None], id='no tfgraph')
    ])
    def test_load_invalid_sources(self, mocked_abacus, mocked_graph):
        # GIVEN mocked invalid results for loading abacus and tfgraph

        # WHEN AbacusLoader::load is invoked
        # THEN a LoadingIacFileError is raised
        with raises(LoadingIacFileError) as error:
            AbacusLoader(sources=[get_bytes('MOCKED')] * 2).load()

        # AND an empty IaC file message is on the exception
        assert str(error.value.title) == 'IaC files are not valid'
        assert str(error.value.message) == 'The provided IaC files could not be processed'
