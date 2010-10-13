import httplib
import urllib
import unittest

import mox

import pubsubsuperfeedr


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