#!/usr/bin/env python
# vim: sw=4 ts=4 expandtab ai

import imp
from StringIO import StringIO
from unittest import TestCase
from mock import Mock, MagicMock, patch
from transmissionrpc.error import TransmissionError

class Test(TestCase):
    def setUp(self):
        self.mod = imp.load_module('torrent', open('torrent'),
                              'torrent', ('', 'r', imp.PY_SOURCE))

        items = {}
        for i in range(7):
            item = MagicMock()
            item.fields = {'name': 'Torrent %i' % i, 'status': i}
            item.eta = 20 * i
            item.progress = 5 * i
            items[i] = item
 
        self.mod.Transmission = Mock()
        self.mod.Transmission.return_value.list.return_value = items

        self.mod.netrc = Mock()
        self.mod.netrc.return_value.authenticators.\
                return_value = ['user', '?', 'password']

        urllib = Mock()
        urllib.urlencode.return_value=''
        self.mod.urllib = urllib
        urllib2 = Mock()
        torrent = Mock()
        torrent.read.return_value = ''
        urllib2.build_opener.return_value.open.return_value=torrent
        self.mod.urllib2 = urllib2

        self.main = self.mod.main

    def test_ls(self):
        with patch('sys.stdout', new_callable=StringIO) as stdout:
            self.main(['ls'])
            assert stdout.getvalue() == """0 Torrent 0 stopped 0 0
1 Torrent 1 check pending 5 20
2 Torrent 2 checking 10 40
3 Torrent 3 download pending 15 60
4 Torrent 4 downloading 20 80
5 Torrent 5 seed pending 25 100
6 Torrent 6 seeding 30 120
"""

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
        assert self.main(['add', 'url']) == None

    def test_transmissionerror(self):
        self.mod.Transmission.return_value.add.side_effect = TransmissionError("message")
        with patch('sys.stdout', new_callable=StringIO) as stdout:
            self.main(['add', 'url'])
            assert stdout.getvalue() == 'Transmission error: message\n'

    def test_usage(self):
        with patch('sys.stdout', new_callable=StringIO) as stdout:
            self.main([])
            assert stdout.getvalue().startswith(self.mod.__doc__)
        with patch('sys.stdout', new_callable=StringIO) as stdout:
            self.main(['add'])
            assert stdout.getvalue().startswith(self.mod.__doc__)

    def test_netrcerrors(self):
        self.mod.netrc.return_value.authenticators.return_value = None
        assert self.main(['ls']) == 1
        self.mod.netrc.side_effect = IOError()
        assert self.main(['ls']) == 1
