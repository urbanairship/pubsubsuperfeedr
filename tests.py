from __future__ import absolute_import
import datetime
import mock
from six.moves import http_client
from six.moves import urllib
import unittest

import dateutil.tz

from pubsubsuperfeedr import Superfeedr


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
"""  # noqa


class TestPubSubSuperfeedr(unittest.TestCase):

    def setUp(self):
        self.feed_url = "http://example.com/feed"
        self.callback_url = "http://example.com/callback"
        self.secret = "my_secret"
        super(TestPubSubSuperfeedr, self).setUp()

    @mock.patch.object(Superfeedr, '_get_connection')
    def test_post_to_superfeedr(self, get_conn_mock):
        conn_mock = mock.Mock(spec=http_client.HTTPSConnection)
        get_conn_mock.return_value = conn_mock

        sf = Superfeedr("foo", "bar")

        data = {"foo": "bar"}
        expected_post_data = urllib.parse.urlencode(data)
        expected_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic Zm9vOmJhcg==",  # foo:bar in basic auth
            "User-Agent": sf.user_agent
        }

        sf.post_to_superfeedr(data)
        conn_mock.request.assert_called_with(
            "POST", "/hubbub", expected_post_data, expected_headers
        )
        conn_mock.getresponse.assert_called_with()

    @mock.patch.object(Superfeedr, 'post_to_superfeedr')
    def test_add_feed(self, post_mock):
        sf = Superfeedr("foo", "bar")
        expected_data = {
            "hub.mode": "subscribe",
            "hub.callback": self.callback_url,
            "hub.topic": self.feed_url,
            "hub.verify": "sync",
            "hub.verify_token": "",
            "hub.secret": self.secret
        }

        sf.add_feed(self.feed_url, self.callback_url, secret=self.secret)
        post_mock.assert_called_with(expected_data)

    @mock.patch.object(Superfeedr, 'post_to_superfeedr')
    def test_remove_feed(self, post_mock):
        sf = Superfeedr("foo", "bar")
        expected_data = {
            "hub.mode": "unsubscribe",
            "hub.callback": self.callback_url,
            "hub.topic": self.feed_url,
            "hub.verify": "sync",
            "hub.verify_token": "",
            "hub.secret": self.secret
        }

        sf.remove_feed(self.feed_url, self.callback_url, secret=self.secret)
        post_mock.assert_called_with(expected_data)

    def test_verify_secret(self):
        sf = Superfeedr("foo", "bar")
        feed_data = "foobar!"
        hmac_header = "sha1=ea7283bf6f519ef24cec649451f43d223f6e2825"
        self.assertTrue(sf.verify_secret(self.secret, feed_data,
                                         hmac_header))

    def test_parse_status_schema(self):
        sf = Superfeedr("foo", "bar")
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

        self.assertEqual(sf.parse_status_schema(example_status_schema),
                         expected_values)

    @mock.patch.object(Superfeedr, 'post_to_superfeedr')
    def test_get_status_of_feed(self, post_mock):
        resp = mock.Mock()
        resp.read.return_value = example_status_schema
        post_mock.return_value = resp

        sf = Superfeedr("foo", "bar")

        data = {
            "hub.mode": "retrieve",
            "hub.topic": self.feed_url
        }

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

        status_data = sf.get_status_of_feed(self.feed_url)

        self.assertEqual(status_data, expected_values)
        post_mock.assert_called_with(data, method="GET")
        resp.read.assert_called_with()

    @mock.patch.object(Superfeedr, 'post_to_superfeedr')
    def test_get_status_of_untracked_feed(self, post_mock):
        resp = mock.Mock()
        resp.read.return_value = ""
        post_mock.return_value = resp

        sf = Superfeedr("foo", "bar")

        data = {
            "hub.mode": "retrieve",
            "hub.topic": self.feed_url
        }

        status_data = sf.get_status_of_feed(self.feed_url)

        self.assertIsNone(status_data)
        post_mock.assert_called_with(data, method="GET")
        resp.read.assert_called_with()
