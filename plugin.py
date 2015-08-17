###
# Copyright (c) 2015, Moritz Lipp
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import json

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.ircmsgs as ircmsgs
import supybot.callbacks as callbacks
import supybot.log as log
import supybot.httpserver as httpserver
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Taiga')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class TaigaHandler(object):
    def __init__(self, irc, channel):
        self.irc = irc
        self.channel = channel
        self.log = log.getPluginLogger('Taiga')

    def handle_payload(self, payload):
        if 'type' not in payload:
            return
        if 'action' not in payload:
            return
        if 'data' not in payload:
            return

        try:
            handlers = {
                "milestone": self._handle_milestone,
                "userstory": self._handle_userstory,
                "task":      self._handle_task,
                "issue":     self._handle_issue,
                "wikipage":  self._handle_wikipage,
                "test":      self._handle_test
            }

            method = handlers.get(payload['type'], None)
            method(payload)
        except NameError:
            self.log.debug("Unhandled type: '%s'" % payload['type'])
            return

    def _send_message(self, msg):
        msg = ircmsgs.privmsg(self.channel, msg)
        self.irc.queueMsg(msg)

    def _handle_milestone(self, payload):
        user = payload['data']['owner']['name']
        name = payload['data']['name']
        action = payload['action']

        msg = "Milestone '%s' %sd by %s" % (name, action, user)
        self._send_message(msg)
        pass

    def _handle_userstory(self, payload):
        pass

    def _handle_task(self, payload):
        pass

    def _handle_issue(self, payload):
        pass

    def _handle_wikipage(self, payload):
        pass

    def _handle_test(self, payload):
        pass


class TaigaWebHookService(httpserver.SupyHTTPServerCallback):
    """http://taigaio.github.io/taiga-doc/dist/webhooks.html"""

    name = "TaigaWebHookService"
    defaultResponse = """This plugin handles only POST request, please don't use other requests."""

    def __init__(self, plugin, irc):
        self.log = log.getPluginLogger('Taiga')
        self.channel = plugin.registryValue('channel')
        self.taiga = TaigaHandler(irc, self.channel)
        self.secret_key = plugin.registryValue('secret-key')
        self.verify_signature = plugin.registryValue('verify-signature')

    def _verify_signature(self, key, data, signature):
        mac = hmac.new(key.encode("utf-8"), msg=data, digestmod=hashlib.sha1)
        return mac.hexdigest() == signature

    def _send_error(self, handler, message):
        handler.send_response(403)
        handler.send_header('Content-type', 'text/plain')
        handler.end_headers()
        handler.wfile.write(message.encode('utf-8'))

    def _send_ok(self, handler):
        handler.send_response(200)
        handler.send_header('Content-type', 'text/plain')
        handler.end_headers()
        handler.wfile.write(bytes('OK', 'utf-8'))

    def doPost(self, handler, path, form):
        headers = dict(self.headers)

        # Check for Taiga webhook signature
        if self.verify_signature is True:
            if 'X-TAIGA-WEBHOOK-SIGNATURE' not in headers:
                self._send_error(handler, _("""Error: No signature provided."""))
                return

            # Verify signature
            signature = headers['X-TAIGA-WEBHOOK-SIGNATURE']
            if self._verify_signature(self.secret_key, data, signature) is False:
                self._send_error(handler, _("""Error: Invalid signature."""))
                return

        # Handle payload
        try:
            payload = json.loads(form.decode('utf-8'))
            self.taiga.handle_payload(payload)
        except Exception as e:
            print(e)
            self._send_error(handler, _("""Error: Invalid data sent."""))

        # Return OK
        self._send_ok(handler)


class Taiga(callbacks.Plugin):
    """Plugin for communication and notifications of a Taiga project management tool instance"""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(Taiga, self)
        self.__parent.__init__(irc)

        callback = TaigaWebHookService(self, irc)
        httpserver.hook('taiga', callback)

    def die(self):
        httpserver.unhook('taiga')

        self.__parent.die()


Class = Taiga


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
