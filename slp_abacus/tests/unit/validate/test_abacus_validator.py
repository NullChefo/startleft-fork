import random
from typing import List

import pytest
from pytest import mark, param, fixture

from slp_base import IacFileNotValidError
from slp_abacus.slp_abacus.validate.abacus_validator import AbacusValidator
from sl_util.sl_util.str_utils import get_bytes
from slp_abacus.tests.util.builders import create_artificial_file, MIN_FILE_SIZE, MAX_ABACUS_FILE_SIZE, \
    MAX_TFGRAPH_FILE_SIZE

MINIMUM_VALID_ABACUS_SOURCE = get_bytes('{"planned_values":{"root_module":{"resources":[]}},"configuration":{}}',
                                        'utf-8')
MINIMUM_VALID_TFGRAPH_SOURCE = get_bytes('digraph {subgraph "root" {}}', 'utf-8')

ABACUS_VALID_MIME = 'application/json'
TFGRAPH_VALID_MIME = 'text/plain'
VALID_MIME_TYPES = [ABACUS_VALID_MIME, TFGRAPH_VALID_MIME]


@fixture(autouse=True)
def mocked_mime_types():
    yield VALID_MIME_TYPES


@fixture
def mock_mime_checker(mocker, mocked_mime_types):
    mocker.patch('magic.Magic.from_buffer', side_effect=mocked_mime_types)


class TestAbacusValidator:

    def test_valid_abacus_and_tfgraph(self):
        # GIVEN a valid abacus
        abacus = MINIMUM_VALID_ABACUS_SOURCE

        # AND a valid tfgraph
        tfgraph = MINIMUM_VALID_TFGRAPH_SOURCE

        # WHEN AbacusValidator::validate is invoked
        AbacusValidator([abacus, tfgraph]).validate()

        # THEN no error is raised

    @mark.parametrize('sources', [
        param([], id='no sources'),
        param([MINIMUM_VALID_ABACUS_SOURCE], id='missing one source'),
        param([MINIMUM_VALID_ABACUS_SOURCE] * random.randint(3, 10), id='more than two sources'),
    ])
    def test_wrong_number_of_sources(self, sources: List[bytes]):
        # GIVEN a wrong number of sources

        # WHEN AbacusValidator::validate is invoked
        # THEN a IacFileNotValidError is raised
        with pytest.raises(IacFileNotValidError) as error:
            AbacusValidator(sources).validate()

        # AND whose information is right
        assert error.value.title == 'Wrong number of files'
        assert error.value.message == 'Required one abacus and one tfgraph files'

    def test_two_abacus(self):
        # GIVEN two abacus files
        sources = [MINIMUM_VALID_ABACUS_SOURCE, MINIMUM_VALID_ABACUS_SOURCE]

        # WHEN AbacusValidator::validate is invoked
        # THEN a IacFileNotValidError is raised
        with pytest.raises(IacFileNotValidError) as error:
            AbacusValidator(sources).validate()

        # AND whose information is right
        assert error.value.title == 'Two abacus files'
        assert error.value.message == 'Required one abacus and one tfgraph files'

    @mark.usefixtures('mock_mime_checker')
    @mark.parametrize('sources', [
        param([create_artificial_file(MIN_FILE_SIZE - 1), MINIMUM_VALID_TFGRAPH_SOURCE], id='abacus too small'),
        param([create_artificial_file(MAX_ABACUS_FILE_SIZE + 1), MINIMUM_VALID_TFGRAPH_SOURCE], id='abacus too big'),
        param([MINIMUM_VALID_ABACUS_SOURCE, create_artificial_file(MIN_FILE_SIZE - 1)], id='tfgraph too small'),
        param([MINIMUM_VALID_ABACUS_SOURCE, create_artificial_file(MAX_TFGRAPH_FILE_SIZE + 1)], id='tfgraph too big')
    ])
    def test_invalid_size(self, sources: List[bytes]):
        # GIVEN a abacus with an invalid size

        # WHEN AbacusValidator::validate is invoked
        # THEN a IacFileNotValidError is raised
        with pytest.raises(IacFileNotValidError) as error:
            AbacusValidator(sources).validate()

        # AND whose information is right
        assert error.value.title == 'Terraform Plan file is not valid'
        assert error.value.message == 'Provided iac_file is not valid. Invalid size'

    @mark.usefixtures('mock_mime_checker')
    @mark.parametrize('mocked_mime_types', [
        param(['text/xml', 'text/plain'], id='abacus wrong'),
        param(['application/json', 'text/xml'], id='tfgraph wrong'),
        param(['text/xml', 'text/xml'], id='both wrong')
    ])
    def test_invalid_file_type(self, mocked_mime_types: List[str]):
        # GIVEN a abacus with an invalid size
        mocked_sources = [create_artificial_file(len(MINIMUM_VALID_ABACUS_SOURCE)),
                          create_artificial_file(len(MINIMUM_VALID_TFGRAPH_SOURCE))]

        # WHEN AbacusValidator::validate is invoked
        # THEN a IacFileNotValidError is raised
        with pytest.raises(IacFileNotValidError) as error:
            AbacusValidator(mocked_sources).validate()

        # AND whose information is right
        assert error.value.title == 'Terraform Plan file is not valid'
        assert error.value.message == 'Invalid content type for iac_file'

    @mark.parametrize('abacus,tfgraph', [
        param(get_bytes('{"invalid": "abacus"}'), MINIMUM_VALID_TFGRAPH_SOURCE, id='invalid abacus'),
        param(MINIMUM_VALID_ABACUS_SOURCE, get_bytes('{"invalid": "tfgraph"}'), id='invalid tfgraph'),
        param(get_bytes('{"invalid": "abacus"}'), get_bytes('{"invalid": "tfgraph"}'), id='both invalid')
    ])
    def test_wrong_sources(self, abacus: bytes, tfgraph: bytes):
        # GIVEN a valid tfgraph and wrong abacus or vice-versa

        # WHEN AbacusValidator::validate is invoked
        # THEN a IacFileNotValidError is raised
        with pytest.raises(IacFileNotValidError) as error:
            AbacusValidator([abacus, tfgraph]).validate()

        # AND whose information is right
        assert error.value.title == 'Terraform Plan file is not valid'
        assert error.value.message == 'Invalid content type for iac_file'
