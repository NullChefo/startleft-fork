import os

path = os.path.dirname(__file__)

# generic
invalid_yaml = path + '/generic/invalid-yaml.yaml'

# abacus
abacus_elb = path + '/abacus/elb-abacus.json'
abacus_sgs = path + '/abacus/sgs-abacus.json'
abacus_official = path + '/abacus/official-abacus.json'

# resources abacus
# ingress_cidr_from_property = path + '/abacus/resources/ingress-cidr-from-property-abacus-resources.json'
# ingress_multiple_cidr_from_property = path + \
#                                       '/abacus/resources/ingress-multiple-cidr-from-property-abacus-resources.json'
# ingress_multiple_cidr_from_rule = path + '/abacus/resources/ingress-multiple-cidr-from-rule-abacus-resources.json'
# ingress_multiple_security_groups = path + '/abacus/resources/ingress-multiple-security-groups-abacus-resources.json'
#

# mapping
terraform_iriusrisk_abacus_aws_mapping = path + '/mapping/iriusrisk-abacus-aws-mapping.yaml'

# otm
otm_expected_elb = f'{path}/otm/expected-elb.otm'
otm_expected_sgs = f'{path}/otm/expected-sgs.otm'
otm_expected_official = f'{path}/otm/expected-official.otm'

