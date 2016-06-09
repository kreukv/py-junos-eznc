import unittest2 as unittest
from nose.plugins.attrib import attr
from mock import MagicMock, patch
import re
import sys

from jnpr.junos.console import Console
from jnpr.junos.transport.tty_netconf import tty_netconf
from jnpr.junos.transport.tty_telnet import Telnet

if sys.version<'3':
    builtin_string = '__builtin__'
else:
    builtin_string = 'builtins'

@attr('unit')
class TestConsole(unittest.TestCase):

    @patch('jnpr.junos.transport.tty_telnet.Telnet._tty_open')
    @patch('jnpr.junos.transport.tty_telnet.telnetlib.Telnet.expect')
    @patch('jnpr.junos.transport.tty_telnet.Telnet.write')
    def setUp(self, mock_write, mock_expect, mock_open):
        tty_netconf.open = MagicMock()
        mock_expect.side_effect=[(1, re.search('(?P<login>ogin:\s*$)', "login: "), '\r\r\nbng-ui-vm-92 login:'),
                                (2, re.search('(?P<passwd>assword:\s*$)', "password: "), '\r\r\nbng-ui-vm-92 passd:'),
                                 (3, re.search('(?P<shell>%|#\s*$)', "junos % "), '\r\r\nbng-ui-vm-92 junos %')]


        self.dev = Console(host='1.1.1.1', user='lab', password='lab123', mode = 'Telnet')
        self.dev.open()

    @patch('jnpr.junos.console.Console._tty_logout')
    def tearDown(self, mock_tty_logout):
        self.dev.close()

    @patch('jnpr.junos.console.Console._tty_login')
    def test_console_open_error(self, mock_tty_login):
        mock_tty_login.side_effect = RuntimeError
        self.assertRaises(RuntimeError, self.dev.open)

    def test_console_connected(self):
        self.assertTrue(self.dev.connected)
        self.assertFalse(self.dev.gather_facts)

    @patch('jnpr.junos.console.Console._tty_logout')
    def test_console_close_error(self, mock_logout):
        mock_logout.side_effect = RuntimeError
        self.assertRaises(RuntimeError, self.dev.close)

    # @patch('jnpr.junos.transport.tty_telnet.Telnet._tty_close')
    # def test_console_close_error2(self, mock_close):
    #     mock_close.side_effect = RuntimeError
    #     self.assertRaises(RuntimeError, self.dev.close(True))

    @patch('jnpr.junos.transport.tty_netconf.tty_netconf.rpc')
    def test_console_zeroize(self, mock_zeroize):
        self.dev.zeroize()
        self.assertTrue(mock_zeroize.called)

    @patch('jnpr.junos.transport.tty_netconf.tty_netconf.rpc')
    @patch('jnpr.junos.console.FACT_LIST')
    def test_console_gather_facts(self, mock_fact_list, mock_rpc):
        from jnpr.junos.facts.session import facts_session
        mock_fact_list.__iter__.return_value = [facts_session]
        self.dev._gather_facts()
        self.assertEqual(mock_rpc.call_count, 1)



