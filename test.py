#!/usr/bin/env python
# vim: sw=4 ts=4 expandtab ai

import imp
from StringIO import StringIO
from unittest import TestCase
from mock import Mock

import transmissionrpc

class FakeTransmission(object):

    def __init__(self, user, password, timeout=10):
        self.torrent = transmissionrpc.Torrent(self,
                {'id': 1, 'name': 'My torrent', 'status': 0,
                 'sizeWhenDone': 100, 'leftUntilDone': 50,
                 'eta': 20})

    def list(self):
        return {1: self.torrent}

    def add(self, arg):
        if arg == 'MQ==':
            raise transmissionrpc.error.TransmissionError('Error')

    def empty(self, *args, **kwargs):
        pass

    start = stop = remove = set_session = empty

class FakeUrllib(object):
    def __init__(self):
        self.num = 1

    def urlencode(self, *args):
        return '123'

    def read(self, *args):
        self.num ^= 1
        return ['1', '2'][self.num]

    def empty(self, *args):
        return self

    build_opener = install_opener = HTTPCookieProcessor = open = empty

class Test(TestCase):
    def setUp(self):
        self.mod = imp.load_module('torrent', open('torrent'),
                              'torrent', ('', 'r', imp.PY_SOURCE))
        self.mod.Transmission = FakeTransmission
        self.mod.netrc = Mock()
        self.mod.netrc.return_value.authenticators.return_value = ['user', '?', 'password']
        self.mod.sys.stdout = StringIO()
        self.mod.urllib = self.mod.urllib2 = FakeUrllib()

        self.main = self.mod.main

    def test_ls(self):
        self.main(['ls'])
        self.mod.sys.stdout.seek(0)
        assert self.mod.sys.stdout.read() == "1 My torrent stopped 50.0 0:00:20\n"

    def test_start(self):
        self.main(['start', '1'])

    def test_stop(self):
        self.main(['stop', '1'])

    def test_up(self):
        self.main(['up', '10'])
        self.main(['up'])

    def test_down(self):
        self.main(['down', '10'])
        self.main(['down'])
    
    def test_rm(self):
        self.main(['rm', '1'])
    
    def test_add(self):
        assert self.main(['add', 'url']) == 1
        assert self.main(['add', 'url']) == None

    def test_usage(self):
        self.main([])
        self.mod.sys.stdout.seek(0)
        assert self.mod.sys.stdout.read().startswith(self.mod.__doc__)
        self.mod.sys.stdout.seek(0)
        self.main(['add'])
        self.mod.sys.stdout.seek(0)
        assert self.mod.sys.stdout.read().startswith(self.mod.__doc__)

