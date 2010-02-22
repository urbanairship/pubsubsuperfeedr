"""Library for adding/removing feeds with Superfeedr's PubSubHubbub API"""
import hashlib
import hmac
import httplib
import urllib

import feedparser


class Superfeedr(object):

    def __init__(self, superfeedr_username, superfeedr_password,
            user_agent=None):
        if user_agent is None:
            user_agent = "PythonSuperfeedr/0.1"
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

    def post_to_superfeedr(self, data):
        """Communicates with Superfeedr's hubbub endpoint"""
        form_data = urllib.urlencode(data)
        auth_string = ('%s:%s' % (self.superfeedr_username,
            self.superfeedr_password)).encode("base64")[:-1]
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic %s" % auth_string,
            "User-Agent": self.user_agent
        }
        conn = httplib.HTTPSConnection("superfeedr.com")
        conn.request("POST", "/hubbub", form_data, headers)
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
