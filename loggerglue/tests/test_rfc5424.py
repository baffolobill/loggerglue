import unittest
from datetime import datetime
from pyparsing import ParseException

from loggerglue.rfc5424 import (
    syslog_msg, SyslogEntry, SDElement, StructuredData
)
from loggerglue.util.MultiDict import OrderedMultiDict


valids = (
    """<34>1 2003-10-11T22:14:15.003Z mymachine.example.com su - ID47 - \xef\xbb\xbf'su root' failed for lonvick on /dev/pts/8""",
    """<165>1 2003-08-24T05:14:15.000003-07:00 192.0.2.1 myproc 8710 - - %% It's time to make the do-nuts.""",
    """<165>1 2003-10-11T22:14:15.003Z mymachine.example.com evntslog - ID47 [exampleSDID@32473 iut="3" eventSource="Application" eventID="1011"] \xef\xbb\xbfAn application event log entry...""",
    """<165>1 2003-10-11T22:14:15.003Z mymachine.example.com evntslog - ID47 [exampleSDID@32473 iut="3" eventSource="Application" eventID="1011"][examplePriority@32473 class="high"]""",
    """<165>1 2003-10-11T22:14:15.003Z mymachine.example.com evntslog - ID47 [traceback@32473 file="main.py" line="123" method="runStuff" file="pinger.py" line="456" method="pingpong"]""",
    """<34>1 2003-10-11T22:14:15.003000Z mymachine.example.com su - ID47 [test@32473 escaped="\\"nS\\]t\\u\n"] \xef\xbb\xbf'su root' failed\n for lonvick on /dev/pts/8""",
    """<165>1 2003-10-11T22:14:15.003000Z mymachine.example.com evntslog - ID47 [exampleSDID@32473 iut="3" eventSource="Application" eventID="1011"] \xef\xbb\xbfAn application event log entry...""",
    """<78>1 2011-03-20T12:00:01+01:00 mymachine.example.com - 9778 - - (orion) CMD (/home/www/stats/pinger.py /home/www/stats/data/pinger.pickle)""",
    )

invalids = (
    """This is obviously invalid.""",
    )


class TestABNF(unittest.TestCase):
    def test_valids(self):
        for v in valids:
            syslog_msg.parseString(v)

    def test_invalids(self):
        for i in invalids:
            self.assertRaises(ParseException, syslog_msg.parseString, i)

    def test_details_0(self):
        r = syslog_msg.parseString(valids[0])
        self.assertEqual(r.PRIVAL, '34')
        self.assertEqual(r.VERSION, '1')
        self.assertEqual(r.TIMESTAMP, '2003-10-11T22:14:15.003Z')
        self.assertEqual(r.HOSTNAME, 'mymachine.example.com')
        self.assertEqual(r.APP_NAME, 'su')
        self.assertEqual(r.PROCID, '-')

        self.assertEqual(list(r.STRUCTURED_DATA), ['-'])
        self.assertEqual(r.MSG,
                "\xef\xbb\xbf'su root' failed for lonvick on /dev/pts/8")

    def test_details_2(self):
        r = syslog_msg.parseString(valids[2])
        self.assertTrue(hasattr(r.STRUCTURED_DATA, 'SD_ID'))

    def test_details_3(self):
        r = syslog_msg.parseString(valids[3])
        self.assertEqual(len(r.SD_ELEMENTS), 2)
        self.assertEqual(len(r.SD_ELEMENTS[0].SD_PARAMS), 3)
        self.assertEqual(len(r.SD_ELEMENTS[1].SD_PARAMS), 1)


class TestSDElement(unittest.TestCase):
    def test_init_with_tuples(self):
        e = SDElement('exampleSDID@32473', [('param1', 1), ('param2', 2)])
        self.assertEqual('exampleSDID@32473', e.id)
        self.assertEqual(OrderedMultiDict([('param1', 1), ('param2', 2)]), e.sd_params)
        self.assertEqual('[exampleSDID@32473 param1="1" param2="2"]', str(e))

    def test_init_with_dict(self):
        e = SDElement('exampleSDID@32473', {'param1': 1, 'param2': 2})
        self.assertEqual('exampleSDID@32473', e.id)
        self.assertEqual(OrderedMultiDict({'param1': 1, 'param2': 2}), e.sd_params)


class TestStructuredData(unittest.TestCase):
    def test_init_with_elements(self):
        e = SDElement('exampleSDID@32473', [('param1', 1), ('param2', 2)])
        sd = StructuredData([e])
        self.assertEqual('[exampleSDID@32473 param1="1" param2="2"]', str(sd))


class TestSyslogEntry(unittest.TestCase):
    def test_class(self):
        for v in valids:
            se = SyslogEntry.from_line(v)
            self.assertTrue(se is not None)

    def test_details(self):
        se = SyslogEntry.from_line(valids[0])
        self.assertEqual(se.msg,
                """'su root' failed for lonvick on /dev/pts/8""")
        self.assertEqual(se.timestamp.year, 2003)
        self.assertEqual(se.hostname, 'mymachine.example.com')
        self.assertEqual(se.msgid, 'ID47')

        se = SyslogEntry.from_line(valids[3])
        self.assertEqual(len(se.structured_data.elements), 2)
        self.assertEqual(len(se.structured_data.elements[0].sd_params), 3)
        self.assertEqual(len(se.structured_data.elements[1].sd_params), 1)

        se = SyslogEntry.from_line(valids[4])
        self.assertEqual(len(se.structured_data.elements), 1)
        self.assertEqual(len(list(se.structured_data.elements[0].sd_params.allitems())), 6)
        self.assertEqual(len(list(se.structured_data.elements[0].sd_params.getall("file"))), 2)

        se = SyslogEntry.from_line(valids[5])
        self.assertEqual(str(se), valids[5])

        se = SyslogEntry(
                prival=165, version=1, timestamp=datetime(2003,10,11,22,14,15,3000),
                hostname='mymachine.example.com', app_name='evntslog', procid=None, msgid='ID47',
                structured_data=StructuredData([SDElement('exampleSDID@32473',
                    [('iut','3'),
                    ('eventSource','Application'),
                    ('eventID','1011')]
                    )]),
                msg=u'An application event log entry...'
        )
        self.assertEqual(str(se), valids[6])

        se = SyslogEntry.from_line(valids[7])
        self.assertEqual(se.timestamp.year, 2011)


class TestSyslogEntry(unittest.TestCase):
    def test_float_timestamp(self):
        se = SyslogEntry(timestamp=datetime(2003,10,11,22,14,15,3000))
        self.assertEqual('<14>1 2003-10-11T22:14:15.003000Z - - - - -', str(se))
        se.timestamp_as_float = True
        self.assertEqual('<14>1 1065910455.003 - - - - -', str(se))


if __name__ == '__main__':
    unittest.main()
