import random
from typing import List

import pytest
from pytest import mark, param

from slp_base import IacFileNotValidError
from sl_util.sl_util.file_utils import get_byte_data
from slp_abacus import AbacusProcessor
from slp_abacus.tests.resources.test_resource_paths import terraform_iriusrisk_abacus_aws_mapping, \
    abacus_elb, tfgraph_elb, abacus_sgs, tfgraph_sgs, otm_expected_sgs, otm_expected_elb, \
    otm_expected_official, abacus_official, tfgraph_official, invalid_yaml
from slp_base.tests.util.otm import validate_and_compare
from slp_abacus.tests.util.builders import create_artificial_file, MIN_FILE_SIZE, MAX_ABACUS_FILE_SIZE, \
    MAX_TFGRAPH_FILE_SIZE

DEFAULT_MAPPING_FILE = get_byte_data(terraform_iriusrisk_abacus_aws_mapping)

SAMPLE_VALID_ABACUS = get_byte_data(abacus_elb)
SAMPLE_VALID_TFGRAPH = get_byte_data(tfgraph_elb)

SAMPLE_INVALID_ABACUS = get_byte_data(invalid_yaml)
SAMPLE_INVALID_TFGRAPH = get_byte_data(invalid_yaml)

SAMPLE_ID = 'id'
SAMPLE_NAME = 'name'
EXCLUDED_REGEX = r"root\[\'dataflows'\]\[.+?\]\['id'\]"


class TestAbacus:

    @mark.parametrize('abacus,tfgraph,expected',
                      [param(get_byte_data(abacus_elb), get_byte_data(tfgraph_elb), otm_expected_elb,
                             id='elb-example'),
                       param(get_byte_data(abacus_sgs), get_byte_data(tfgraph_sgs), otm_expected_sgs,
                             id='sgs-example'),
                       param(get_byte_data(abacus_official), get_byte_data(tfgraph_official),
                             otm_expected_official,
                             id='official-example')])
    def test_abacus_tfgraph_examples(self, abacus: bytes, tfgraph: bytes, expected: str):
        # GIVEN a valid ABACUS file and a valid tfgraph
        # AND a valid TF mapping file
        mapping_file = DEFAULT_MAPPING_FILE

        # WHEN AbacusProcessor::process is invoked
        otm = AbacusProcessor(SAMPLE_ID, SAMPLE_NAME, [abacus, tfgraph], [mapping_file]).process()

        # THEN the resulting OTM match the expected one
        left, right = validate_and_compare(otm, expected, EXCLUDED_REGEX)
        assert left == right

    @mark.parametrize('sources', [
        param([], id='no sources'),
        param([SAMPLE_VALID_ABACUS], id='one source'),
        param([SAMPLE_VALID_ABACUS] * random.randint(3, 10), id='more than two sources')
    ])
    def test_wrong_number_of_parameters(self, sources: List[bytes]):
        # GIVEN a wrong number of sources

        # WHEN AbacusProcessor::process is invoked
        # THEN a LoadingIacFileError exception is raised
        with pytest.raises(IacFileNotValidError) as error:
            AbacusProcessor(SAMPLE_ID, SAMPLE_NAME, sources, [DEFAULT_MAPPING_FILE]).process()

        # AND the message says that the number of parameters is wrong
        assert str(error.value.title) == 'Wrong number of files'
        assert str(error.value.message) == 'Required one abacus and one tfgraph files'

    @mark.parametrize('sources', [
        param([create_artificial_file(MIN_FILE_SIZE - 1), SAMPLE_VALID_TFGRAPH], id='abacus too small'),
        param([create_artificial_file(MAX_ABACUS_FILE_SIZE + 1), SAMPLE_VALID_TFGRAPH], id='abacus too big'),
        param([SAMPLE_VALID_ABACUS, create_artificial_file(MIN_FILE_SIZE - 1)], id='tfgraph too small'),
        param([SAMPLE_VALID_ABACUS, create_artificial_file(MAX_TFGRAPH_FILE_SIZE + 1)], id='tfgraph too big')
    ])
    def test_invalid_size(self, sources: List[bytes]):
        # GIVEN a abacus or tfgraph with an invalid size

        # WHEN AbacusProcessor::process is invoked
        # THEN a IacFileNotValidError is raised
        with pytest.raises(IacFileNotValidError) as error:
            AbacusProcessor(SAMPLE_ID, SAMPLE_NAME, sources, [DEFAULT_MAPPING_FILE]).process()

        # AND whose information is right
        assert error.value.title == 'Terraform Plan file is not valid'
        assert error.value.message == 'Provided iac_file is not valid. Invalid size'

    def test_two_abacus(self):
        # GIVEN two valid ABACUSs
        sources = [SAMPLE_VALID_ABACUS, SAMPLE_VALID_ABACUS]

        # WHEN AbacusProcessor::process is invoked
        # THEN a LoadingIacFileError exception is raised
        with pytest.raises(IacFileNotValidError) as error:
            AbacusProcessor(SAMPLE_ID, SAMPLE_NAME, sources, [DEFAULT_MAPPING_FILE]).process()

        # AND the message says that no multiple abacus files can be processed at the same time
        assert str(error.value.title) == 'Two abacus files'
        assert str(error.value.message) == 'Required one abacus and one tfgraph files'

    @mark.parametrize('sources', [
        param([SAMPLE_INVALID_ABACUS, SAMPLE_VALID_TFGRAPH], id='invalid abacus'),
        param([SAMPLE_VALID_ABACUS, SAMPLE_INVALID_TFGRAPH], id='invalid tfgraph'),
        param([SAMPLE_INVALID_ABACUS, SAMPLE_INVALID_TFGRAPH], id='both invalid')
    ])
    def test_invalid_sources(self, sources: List[bytes]):
        # GIVEN some invalid abacus

        # WHEN AbacusProcessor::process is invoked
        # THEN a LoadingIacFileError exception is raised
        with pytest.raises(IacFileNotValidError) as error:
            AbacusProcessor(SAMPLE_ID, SAMPLE_NAME, sources, [DEFAULT_MAPPING_FILE]).process()

        # AND the message says that no multiple abacus files can be processed at the same time
        assert str(error.value.title) == 'Terraform Plan file is not valid'
        assert str(error.value.message) == 'Invalid content type for iac_file'
