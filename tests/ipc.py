# encoding=UTF-8
# Copyright © 2010 Jakub Wilk <jwilk@jwilk.net>
#
# This package is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This package is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

from __future__ import with_statement

import os
import signal
import stat

from tests.common import *

from lib import ipc
from lib import temporary

class test_wait():

    def test0(self):
        child = ipc.Subprocess(['true'])
        child.wait()

    def test1(self):
        child = ipc.Subprocess(['false'])
        with raises(ipc.CalledProcessError, "Command 'false' returned non-zero exit status 1"):
            child.wait()

    def _test_signal(self, name):
        child = ipc.Subprocess(['cat']) # Any long-standing process would do.
        os.kill(child.pid, getattr(signal, name))
        with raises(ipc.CalledProcessInterrupted, "Command 'cat' was interrputed by signal " + name):
            child.wait()

    def test_wait_signal(self):
        for name in 'SIGINT', 'SIGABRT', 'SIGSEGV':
            yield self._test_signal, name

class test_environment():

    # http://bugs.debian.org/594385

    def test1(self):
        with amended_environment(ocrodjvu='42'):
            child = ipc.Subprocess(
                ['sh', '-c', 'printf $ocrodjvu'],
                stdout=ipc.PIPE, stderr=ipc.PIPE,
            )
            stdout, stderr = child.communicate()
            assert_equal(stdout, '42')
            assert_equal(stderr, '')

    def test2(self):
        with amended_environment(ocrodjvu='42'):
            child = ipc.Subprocess(
                ['sh', '-c', 'printf $ocrodjvu'],
                stdout=ipc.PIPE, stderr=ipc.PIPE,
                env={},
            )
            stdout, stderr = child.communicate()
            assert_equal(stdout, '42')
            assert_equal(stderr, '')

    def test3(self):
        with amended_environment(ocrodjvu='42'):
            child = ipc.Subprocess(
                ['sh', '-c', 'printf $ocrodjvu'],
                stdout=ipc.PIPE, stderr=ipc.PIPE,
                env=dict(ocrodjvu='24'),
            )
            stdout, stderr = child.communicate()
            assert_equal(stdout, '24')
            assert_equal(stderr, '')

    def test_path(self):
        path = os.getenv('PATH').split(':')
        with temporary.directory() as tmpdir:
            command_name = temporary.name(dir=tmpdir)
            command_path = os.path.join(tmpdir, command_name)
            with open(command_path, 'wt') as file:
                print >>file, '#!/bin/sh'
                print >>file, 'printf 42'
            os.chmod(command_path, stat.S_IRWXU)
            path[:0] = [tmpdir]
            path = ':'.join(path)
            with amended_environment(PATH=path):
                child = ipc.Subprocess([command_name],
                    stdout=ipc.PIPE, stderr=ipc.PIPE,
                )
                stdout, stderr = child.communicate()
                assert_equal(stdout, '42')
                assert_equal(stderr, '')

    def _test_locale(self):
        child = ipc.Subprocess(['locale'],
            stdout=ipc.PIPE, stderr=ipc.PIPE
        )
        stdout, stderr = child.communicate()
        stdout = stdout.splitlines()
        stderr = stderr.splitlines()
        assert_equal(stderr, [])
        data = dict(line.split('=', 1) for line in stdout)
        has_lc_all = has_lc_ctype = has_lang = 0
        for key, value in data.iteritems():
            if key == 'LC_ALL':
                has_lc_all = 1
                assert_equal(value, '')
            elif key == 'LC_CTYPE':
                has_lc_ctype = 1
                assert_equal(value, 'en_US.UTF-8')
            elif key == 'LANG':
                has_lang = 1
                assert_equal(value, '')
            else:
                assert_equal(value, '"POSIX"')
        assert_true(has_lc_all)
        assert_true(has_lc_ctype)
        assert_true(has_lang)

    def test_locale_lc_all(self):
        with amended_environment(LC_ALL='en_US.UTF-8'):
            self._test_locale()

    def test_locale_lc_ctype(self):
        with amended_environment(LC_ALL=None, LC_CTYPE='en_US.UTF-8'):
            self._test_locale()

    def test_locale_lang(self):
        with amended_environment(LC_ALL=None, LC_CTYPE=None, LANG='en_US.UTF-8'):
            self._test_locale()

# vim:ts=4 sw=4 et