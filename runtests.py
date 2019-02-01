#!/usr/bin/env python
# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def run_tests(*args, **kwargs):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(**kwargs)
    failures = test_runner.run_tests(args)
    sys.exit(bool(failures))


def process_kwargs(kwarg):
    if len(kwarg.split('=')) == 2:
        return (kwarg.split('=')[0], kwarg.split('=')[1])

    return (kwarg, True)


if __name__ == '__main__':

    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    kwargs = dict(
        process_kwargs(a[2:])
        for a in sys.argv[1:] if a.startswith('--')
    )

    run_tests(*args, **kwargs)
