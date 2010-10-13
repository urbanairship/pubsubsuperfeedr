pubsubsuperfeedr
================

A simple library designed to make it easy to add and remove feeds from
Superfeedr's PubSubHubbub API.  Includes support for hub.secret.

Credits
-------

Developed and used at `Urban Airship <http://urbanairship.com/>`_ and
released under the MIT License.

`Harper Reed's gae-superfeedr-shell
<http://github.com/harperreed/gae-superfeedr-shell/>`_ provided inspiration
for part of this code. Thanks Harper!

Example Usage
-------------

Setting up pubsubsuperfeedr:

    >>> import pubsubsuperfeedr
    >>> sf = pubsubsuperfeedr.Superfeedr(settings.SUPERFEEDR_USERNAME, settings.SUPERFEEDR_PASSWORD)

Validating a feed to make sure that it has at least one readable entry:

    >>> sf.verify_feed_url("http://blog.urbanairship.com/feed/")
    True

Note that this is just a really simple wrapper around feedparser and sometimes
feedparser can read things that Superfeedr can't.

Adding a feed:

    >>> sf.add_feed("http://blog.urbanairship.com/feed/", "http://example.com/your_callback_url", "some_verify_token", "some_secret")

add_feed expects the feed you're wanting to watch, then the callback URL, and
optionally a verify token and feed secret.

Removing a feed:

    >>> sf.remove_feed("http://blog.urbanairship.com/feed/", "http://example.com/your_callback_url", "some_secret")

Removing a feed is basically the same as adding a feed.

Verifying a secret (in Django):

    >>> sf.verify_secret("some_secret", request.raw_post_data, request.META.get("HTTP_X_HUB_SIGNATURE", ""))
    True

Testing
-------

To run the tests, first make sure that `nose
<http://code.google.com/p/python-nose/>`_ and
`mox <http://code.google.com/p/pymox/>`_ are installed. Then:

    $ nosetests

And you're off an running.