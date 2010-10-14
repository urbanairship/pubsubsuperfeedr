"""Library for adding/removing feeds with Superfeedr's PubSubHubbub API"""
__version__ = '0.3.0'

import hashlib
import hmac
import httplib
import urllib

from xml.dom import minidom

import dateutil.parser
import feedparser


class Superfeedr(object):

    def __init__(self, superfeedr_username, superfeedr_password,
            user_agent=None):
        if user_agent is None:
            user_agent = "PubSubSuperfeedr/%s" % __version__
        self.superfeedr_username = superfeedr_username
        self.superfeedr_password = superfeedr_password
        self.user_agent = user_agent

    def verify_feed_url(self, feed_url):
        """Verify that feed_url has feed items.

        Returns False if there aren't feed items, True if there are.

        """
        parsed_data = feedparser.parse(feed_url)
        if not parsed_data.entries:
            return False
        return True

    def _get_connection(self):
        return httplib.HTTPSConnection("superfeedr.com")

    def post_to_superfeedr(self, data, method="POST"):
        """Communicates with Superfeedr's hubbub endpoint"""
        form_data = urllib.urlencode(data)
        auth_string = ('%s:%s' % (self.superfeedr_username,
            self.superfeedr_password)).encode("base64")[:-1]
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic %s" % auth_string,
            "User-Agent": self.user_agent
        }
        conn = self._get_connection()
        conn.request(method, "/hubbub", form_data, headers)
        response = conn.getresponse()
        return response

    def data_template_for_feed(self, feed_url, callback_url,
            verify_token=None, secret=None):
        data = {
            "hub.mode": "",
            "hub.callback": callback_url,
            "hub.topic": feed_url,
            "hub.verify": "sync",
            "hub.verify_token": verify_token or ""
        }
        if secret:
            data["hub.secret"] = secret
        return data

    def add_feed(self, feed_url, callback_url, verify_token=None, secret=None):
        """Add feed_url to Superfeedr with callback_url."""
        data = self.data_template_for_feed(feed_url, callback_url,
            verify_token, secret)
        data["hub.mode"] = "subscribe"
        self.post_to_superfeedr(data)

    def remove_feed(self, feed_url, callback_url, verify_token=None,
            secret=None):
        """Remove feed_url from Superfeedr."""
        data = self.data_template_for_feed(feed_url, callback_url,
            verify_token, secret)
        data["hub.mode"] = "unsubscribe"
        self.post_to_superfeedr(data)

    def verify_secret(self, feed_secret, feed_data, header):
        """Verify the hub secret."""
        hmac_string = "sha1=%s" % hmac.new(str(feed_secret), feed_data,
            hashlib.sha1).hexdigest()
        return hmac_string == header

    def parse_status_schema(self, status_schema):
        """Parses Superfeedr status schema and returns a dictionary"""
        if not status_schema:
            return None
        dom = minidom.parseString(status_schema)
        feed_url = dom.getElementsByTagName(
            "status")[0].getAttribute("feed")
        http_node = dom.getElementsByTagName("http")[0]
        status_code = int(http_node.getAttribute("code"))
        status_info = http_node.firstChild.nodeValue
        next_fetch = dateutil.parser.parse(dom.getElementsByTagName(
            "next_fetch")[0].firstChild.nodeValue)
        last_fetch = dateutil.parser.parse(dom.getElementsByTagName(
            "last_fetch")[0].firstChild.nodeValue)
        last_parse = dateutil.parser.parse(dom.getElementsByTagName(
            "last_parse")[0].firstChild.nodeValue)
        last_maintenance_at = dateutil.parser.parse(dom.getElementsByTagName(
            "last_maintenance_at")[0].firstChild.nodeValue)
        return {
            "feed_url": feed_url,
            "status_code": status_code,
            "status_info": status_info,
            "next_fetch": next_fetch,
            "last_fetch": last_fetch,
            "last_parse": last_parse,
            "last_maintenance_at": last_maintenance_at
        }

    def get_status_of_feed(self, feed_url):
        """Return Superfeedr's status about a particular feed"""
        data = {
            "hub.mode": "retrieve",
            "hub.topic": feed_url
        }
        response = self.post_to_superfeedr(data, method="GET")
        status_schema = response.read()
        return self.parse_status_schema(status_schema)