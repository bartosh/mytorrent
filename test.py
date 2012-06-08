#!/usr/bin/env python
# vim: sw=4 ts=4 expandtab ai

import imp

import mock
import coverage
from nose.tools import ok_, eq_, raises

Tor = imp.load_module('torrent', open('torrent'), 
                      'torrent', ('', 'r', imp.PY_SOURCE))

def test_ls():
    trans = mock.Mock()
    trans.list.return_value = {}
    eq_(Tor.list_torrents(trans, []), None)

def test_start_torrent():
    eq_(Tor.start_torrent(mock.Mock(), []), None)

def test_stop_torrent():
    eq_(Tor.stop_torrent(mock.Mock(), []), None)
