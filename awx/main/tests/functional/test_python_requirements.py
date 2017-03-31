
import os
import re
import pytest
from pip.operations import freeze

from django.conf import settings


@pytest.mark.skip(reason="This test needs some love")
def test_env_matches_requirements_txt():
    def check_is_in(src, dests):
        if src not in dests:
            print("%s not in" % src)
            return False
        return True

    base_dir = settings.BASE_DIR
    requirements_path = os.path.join(base_dir, '../', 'requirements/requirements.txt')

    reqs_actual = []
    xs = freeze.freeze(local_only=True)
    for x in xs:
        if '## The following requirements were added by pip freeze' in x:
            break
        x = x.lower()
        (pkg_name, pkg_version) = x.split('==')
        reqs_actual.append([pkg_name, pkg_version])

    reqs_expected = []
    with open(requirements_path) as f:
        for line in f:
            line = line.partition('#')[0]
            line = line.rstrip().lower()
            # TODO: process git requiremenst and use egg
            if line == '':
                continue
            if line.strip().startswith('#') or line.strip().startswith('git'):
                continue
            if line.startswith('-e'):
                continue

            '''
            Special case pkg_name[pkg_subname]==version
            For this case, we strip out [pkg_subname]
            '''
            (pkg_name, pkg_version) = line.split('==')
            pkg_name = re.sub(r'\[.*\]', '', pkg_name)
            reqs_expected.append([pkg_name, pkg_version])

    not_found = []
    for r in reqs_expected:
        res = check_is_in(r, reqs_actual)
        if res is False:
            not_found.append(r)

    if len(not_found) > 0:
        raise RuntimeError("%s not found in \n\n%s" % (not_found, reqs_actual))


