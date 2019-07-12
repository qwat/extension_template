#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
***************************************************************************
    create_release.py
    ---------------------
    Date                 : October 2017
    Copyright            : (C) 2017 by Matthias Kuhn
    Email                : matthias@opengis.ch
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Matthias Kuhn'
__date__ = 'October 2017'
__copyright__ = '(C) 2017, Matthias Kuhn'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'


import http.client
import os
import json
import subprocess


def create_dumps():
    files = []
    slug = os.environ['TRAVIS_REPO_SLUG']
    extension_name = slug[slug.rfind('/')+1:]

    # Create data-only dumps (with sample data)

    dump = 'qwat-{extension}_v{version}_data_only_sample.backup'.format(
        version=os.environ['TRAVIS_TAG'],
        extension=extension_name)
    print('travis_fold:start:{}'.format(dump))
    print('Creating dump {}'.format(dump))
    dumpfile = '/tmp/{dump}'.format(dump=dump)
    subprocess.check_output(['pg_dump',
                     '--format', 'custom',
                     '--blobs',
                     '--section', 'data',
                     '--compress', '5',
                     '--verbose',
                     '--file', dumpfile,
                     '--schema', 'qwat_dr',
                     '--schema', 'qwat_od',
                     'qwat_prod']
                    )
    files.append(dumpfile)
    print('travis_fold:end:{}'.format(dump))

    dump='qwat-{extension}_v{version}_data_only_sample.sql'.format(
        version=os.environ['TRAVIS_TAG'],
        extension=extension_name)
    print('travis_fold:start:{}'.format(dump))
    print('Creating dump {}'.format(dump))
    dumpfile='/tmp/{dump}'.format(dump=dump)

    subprocess.check_output(['pg_dump',
                     '--format', 'plain',
                     '--blobs',
                     '--section', 'data',
                     '--verbose',
                     '--file', dumpfile,
                     '--schema', 'qwat_dr',
                     '--schema', 'qwat_od',
                     'qwat_prod']
                    )
    files.append(dumpfile)
    print('travis_fold:end:{}'.format(dump))

    # Create data + structure dumps (with sample data)

    dump='qwat-{extension}_v{version}_data_and_structure_sample.backup'.format(
        version=os.environ['TRAVIS_TAG'],
        extension=extension_name)
    print('travis_fold:start:{}'.format(dump))
    print('Creating dump {}'.format(dump))
    dumpfile='/tmp/{dump}'.format(dump=dump)

    subprocess.check_output(['pg_dump',
                     '--format', 'custom',
                     '--blobs',
                     '--compress', '5',
                     '--verbose',
                     '--file', dumpfile,
                     '-N', 'public',
                     'qwat_prod']
                    )
    files.append(dumpfile)
    print('travis_fold:end:{}'.format(dump))

    dump='qwat-{extension}_v{version}_data_and_structure_sample.sql'.format(
        version=os.environ['TRAVIS_TAG'],
        extension=extension_name)
    print('travis_fold:start:{}'.format(dump))
    print('Creating dump {}'.format(dump))
    dumpfile='/tmp/{dump}'.format(dump=dump)

    subprocess.check_output(['pg_dump',
                     '--format', 'plain',
                     '--blobs',
                     '--verbose',
                     '--file', dumpfile,
                     '-N', 'public',
                     'qwat_prod']
                    )
    files.append(dumpfile)
    print('travis_fold:end:{}'.format(dump))

    # Create structure-only dumps

    dump='qwat-{extension}_v{version}_structure_only.backup'.format(
        version=os.environ['TRAVIS_TAG'],
        extension=extension_name)
    print('travis_fold:start:{}'.format(dump))
    print('Creating dump {}'.format(dump))
    dumpfile='/tmp/{dump}'.format(dump=dump)

    subprocess.check_output(['pg_dump',
                     '--format', 'custom',
                     '--schema-only',
                     '--verbose',
                     '--file', dumpfile,
                     '-N', 'public',
                     'qwat_prod']
                    )
    files.append(dumpfile)
    print('travis_fold:end:{}'.format(dump))

    dump='qwat-{extension}_v{version}_structure_only.sql'.format(
        version=os.environ['TRAVIS_TAG'],
        extension=extension_name)
    print('travis_fold:start:{}'.format(dump))
    print('Creating dump {}'.format(dump))
    dumpfile='/tmp/{dump}'.format(dump=dump)

    subprocess.check_output(['pg_dump',
                     '--format', 'plain',
                     '--schema-only',
                     '--verbose',
                     '--file', dumpfile,
                     '-N', 'public',
                     'qwat_prod']
                    )
    files.append(dumpfile)
    print('travis_fold:end:{}'.format(dump))

    # Create value-list data only dumps (the qwat-{extension}_vl schema)

    dump = 'qwat-{extension}_v{version}_value_list_data_only.backup'.format(
        version=os.environ['TRAVIS_TAG'],
        extension=extension_name)
    print('travis_fold:start:{}'.format(dump))
    print('Creating dump {}'.format(dump))
    dumpfile = '/tmp/{dump}'.format(dump=dump)
    subprocess.check_output(['pg_dump',
                     '--format', 'custom',
                     '--blobs',
                     '--compress', '5',
                     '--data-only',
                     '--verbose',
                     '--file', dumpfile,
                     '--schema', 'qwat_vl',
                     'qwat_prod']
                    )
    files.append(dumpfile)
    print('travis_fold:end:{}'.format(dump))

    dump='qwat-{extension}_v{version}_value_list_data_only.sql'.format(
        version=os.environ['TRAVIS_TAG'],
        extension=extension_name)
    print('travis_fold:start:{}'.format(dump))
    print('Creating dump {}'.format(dump))
    dumpfile='/tmp/{dump}'.format(dump=dump)

    subprocess.check_output(['pg_dump',
                     '--format', 'plain',
                     '--blobs',
                     '--data-only',
                     '--verbose',
                     '--file', dumpfile,
                     '--schema', 'qwat_vl',
                     'qwat_prod']
                    )
    files.append(dumpfile)
    print('travis_fold:end:{}'.format(dump))

    return files


def main():
    if 'TRAVIS_TAG' not in os.environ or not os.environ['TRAVIS_TAG']:
        print('No git tag: not deploying anything')
        return
    elif os.environ['TRAVIS_SECURE_ENV_VARS'] != 'true':
        print('No secure environment variables: not deploying anything')
        return
    else:
        print('Creating release from tag {}'.format(os.environ['TRAVIS_TAG']))

    release_files=create_dumps()

if __name__ == "__main__":
    main()
