import datetime
import httplib
import urllib
import unittest

import dateutil.tz
import mox

import pubsubsuperfeedr


# From http://superfeedr.com/documentation#schema
example_status_schema = """
<status feed="http://domain.tld/feed.xml" xmlns="http://superfeedr.com/xmpp-pubsub-ext">
     <http code="200">9718 bytes fetched in 1.462708s : 2 new entries.</http>
     <next_fetch>2010-05-10T11:19:38-07:00</next_fetch>
     <period>900</period>
     <last_fetch>2010-05-10T11:10:38-07:00</last_fetch>
     <last_parse>2010-05-10T11:17:19-07:00</last_parse>
     <last_maintenance_at>2010-05-10T09:45:08-07:00</last_maintenance_at>
     <entries_count_since_last_maintenance>5</entries_count_since_last_maintenance>
     <tilte>Lorem Ipsum</tilte>
</status>
"""


class TestPubSubSuperfeedr(unittest.TestCase):

    __metaclass__ = mox.MoxMetaTestBase

    def setUp(self):
        self.mox = mox.Mox()
        self.sf = pubsubsuperfeedr.Superfeedr("foo", "bar")
        self.resp = self.mox.CreateMockAnything()
        self.feed_url = "http://example.com/feed"
        self.callback_url = "http://example.com/callback"
        self.secret = "my_secret"
        super(TestPubSubSuperfeedr, self).setUp()

    def test_post_to_superfeedr(self):
        self.mox.StubOutWithMock(self.sf, "_get_connection")
        conn = self.mox.CreateMock(httplib.HTTPSConnection)

        data = {"foo": "bar"}
        expected_post_data = urllib.urlencode(data)
        expected_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic Zm9vOmJhcg==", # foo:bar in basic auth
            "User-Agent": self.sf.user_agent
        }

        self.sf._get_connection().AndReturn(conn)
        conn.request("POST", "/hubbub", expected_post_data, expected_headers)
        conn.getresponse().AndReturn(self.resp)

        self.mox.ReplayAll()
        self.sf.post_to_superfeedr(data)
        self.mox.VerifyAll()

    def test_add_feed(self):
        self.mox.StubOutWithMock(self.sf, "post_to_superfeedr")

        expected_data = {
            "hub.mode": "subscribe",
            "hub.callback": self.callback_url,
            "hub.topic": self.feed_url,
            "hub.verify": "sync",
            "hub.verify_token": "",
            "hub.secret": self.secret
        }

        self.sf.post_to_superfeedr(expected_data).AndReturn(self.resp)

        self.mox.ReplayAll()
        self.sf.add_feed(self.feed_url, self.callback_url, secret=self.secret)
        self.mox.VerifyAll()
        
    def test_remove_feed(self):
        self.mox.StubOutWithMock(self.sf, "post_to_superfeedr")

        expected_data = {
            "hub.mode": "unsubscribe",
            "hub.callback": self.callback_url,
            "hub.topic": self.feed_url,
            "hub.verify": "sync",
            "hub.verify_token": "",
            "hub.secret": self.secret
        }

        self.sf.post_to_superfeedr(expected_data).AndReturn(self.resp)

        self.mox.ReplayAll()
        self.sf.remove_feed(self.feed_url, self.callback_url, secret=self.secret)
        self.mox.VerifyAll()

    def test_verify_secret(self):
        feed_data = "foobar!"
        hmac_header = "sha1=ea7283bf6f519ef24cec649451f43d223f6e2825"
        self.assertTrue(self.sf.verify_secret(self.secret, feed_data,
            hmac_header))

    def test_parse_status_schema(self):
        tzinfo = dateutil.tz.tzoffset(None, -25200)
        expected_values = {
            "feed_url": "http://domain.tld/feed.xml",
            "status_code": 200,
            "status_info": "9718 bytes fetched in 1.462708s : 2 new entries.",
            "next_fetch": datetime.datetime(2010, 5, 10, 11, 19, 38,
                tzinfo=tzinfo),
            "last_fetch": datetime.datetime(2010, 5, 10, 11, 10, 38,
                tzinfo=tzinfo),
            "last_parse": datetime.datetime(2010, 5, 10, 11, 17, 19,
                tzinfo=tzinfo),
            "last_maintenance_at": datetime.datetime(2010, 5, 10, 9, 45, 8,
                tzinfo=tzinfo),
        }

        self.assertEqual(self.sf.parse_status_schema(example_status_schema),
            expected_values)

    def test_get_status_of_feed(self):
        self.mox.StubOutWithMock(self.sf, "post_to_superfeedr")

        data = {
            "hub.mode": "retrieve",
            "hub.topic": self.feed_url
        }

        self.sf.post_to_superfeedr(data, method="GET").AndReturn(self.resp)
        self.resp.read().AndReturn(example_status_schema)

        tzinfo = dateutil.tz.tzoffset(None, -25200)
        expected_values = {
            "feed_url": "http://domain.tld/feed.xml",
            "status_code": 200,
            "status_info": "9718 bytes fetched in 1.462708s : 2 new entries.",
            "next_fetch": datetime.datetime(2010, 5, 10, 11, 19, 38,
                tzinfo=tzinfo),
            "last_fetch": datetime.datetime(2010, 5, 10, 11, 10, 38,
                tzinfo=tzinfo),
            "last_parse": datetime.datetime(2010, 5, 10, 11, 17, 19,
                tzinfo=tzinfo),
            "last_maintenance_at": datetime.datetime(2010, 5, 10, 9, 45, 8,
                tzinfo=tzinfo),
        }

        self.mox.ReplayAll()
        status_data = self.sf.get_status_of_feed(self.feed_url)
        self.mox.VerifyAll()

        self.assertEqual(status_data, expected_values)

    def test_get_status_of_untracked_feed(self):
        self.mox.StubOutWithMock(self.sf, "post_to_superfeedr")

        data = {
            "hub.mode": "retrieve",
            "hub.topic": self.feed_url
        }

        self.sf.post_to_superfeedr(data, method="GET").AndReturn(self.resp)
        self.resp.read().AndReturn("")

        expected_values = None

        self.mox.ReplayAll()
        status_data = self.sf.get_status_of_feed(self.feed_url)
        self.mox.VerifyAll()

        self.assertEqual(status_data, expected_values)