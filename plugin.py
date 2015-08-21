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
import hmac
import hashlib

from supybot.commands import *
import supybot.ircdb as ircdb
import supybot.ircmsgs as ircmsgs
import supybot.callbacks as callbacks
import supybot.log as log
import supybot.httpserver as httpserver
try:
    from supybot.i18n import PluginInternationalization
    from supybot.i18n import internationalizeDocstring
    _ = PluginInternationalization('Taiga')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    def _(x):
        return x

    def internationalizeDocstring(x):
        return x


class TaigaHandler(object):
    """Handle taiga messages"""

    def __init__(self, plugin, irc):
        self.irc = irc
        self.plugin = plugin
        self.log = log.getPluginLogger('Taiga')

    def _build_url(self, project_url, project_slug, payload_type, payload):
        appendix = None
        if payload_type == 'milestone':
            appendix = 'taskboard/' + payload['data']['slug']
        elif payload_type == 'userstory':
            appendix = 'us/' + str(payload['data']['id'])
        elif payload_type == 'task':
            appendix = 'us/' + str(payload['data']['user_story'])
        elif payload_type == 'issue':
            appendix = 'issue/' + str(payload['data']['id'])
        elif payload_type == 'wikipage':
            appendix = 'wiki/' + payload['data']['slug']

        return project_url + '/' + appendix

    def handle_payload(self, payload):
        for x in ['type', 'action', 'data']:
            if x not in payload:
                return

        payload_type = payload['type']
        payload_action = payload['action']
        payload_data = payload['data']

        # Do not handle test payloads
        if payload_type == 'test':
            return

        if payload_type not in ['milestone', 'userstory', 'task', 'issue',
                                'wikipage']:
            self.log.debug("Unhandled type: '%s'" % payload_type)
            return

        # Lookup format string
        format_string_identifier = "format.%s-%sd" % (payload_type, payload_action)
        project_id = payload_data['project']

        # Prepare argument data
        data = {
            payload_type: payload_data,
            "project": {
                "id": project_id,
                "name": ""
            },
            "user": payload_data['owner'],
        }

        if payload_type == 'change':
            data['change'] = payload['change']

        # Check if any of the joined channels have subscribed to this project
        for channel in self.irc.state.channels.keys():
            projects = self.plugin._load_projects(channel)
            project_id = str(project_id)
            if project_id in projects.keys():
                # Update with project slug from mapping
                project_slug = projects[project_id]['slug']
                project_url = projects[project_id]['url']
                data['project']['name'] = project_slug
                data['url'] = self._build_url(project_url, project_slug,
                                              payload_type, payload)

                # Send message to channel
                self._send_message(channel, format_string_identifier, data)

    def _send_message(self, channel, format_string_identifier, args):
        format_string = str(self.plugin.registryValue(format_string_identifier, channel))
        msg = format_string.format(**args)
        priv_msg = ircmsgs.privmsg(channel, msg)
        self.irc.queueMsg(priv_msg)


class TaigaWebHookService(httpserver.SupyHTTPServerCallback):
    """http://taigaio.github.io/taiga-doc/dist/webhooks.html"""

    name = "TaigaWebHookService"
    defaultResponse = """This plugin handles only POST request, please don't use other requests."""

    def __init__(self, plugin, irc):
        self.log = log.getPluginLogger('Taiga')
        self.taiga = TaigaHandler(plugin, irc)
        self.plugin = plugin
        self.irc = irc

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

        network = None
        channel = None

        try:
            information = path.split('/')[1:]
            network = information[0]
            channel = '#' + information[1]
        except IndexError:
            self._send_error(handler, _("""Error: You need to provide the
                                        network name and the channel in
                                        url."""))
            return

        if self.irc.network != network or channel in self.irc.state.channels is False:
            return

        secret_key = self.plugin.registryValue('secret-key', channel)
        verify_signature = self.plugin.registryValue('verify-signature', channel)

        # Check for Taiga webhook signature
        if verify_signature is True:
            if 'X-TAIGA-WEBHOOK-SIGNATURE' not in headers:
                self._send_error(handler, _('Error: No signature provided.'))
                return

            # Verify signature
            signature = headers['X-TAIGA-WEBHOOK-SIGNATURE']
            if self._verify_signature(secret_key, form, signature) is False:
                self._send_error(handler, _('Error: Invalid signature.'))
                return

        # Handle payload
        try:
            payload = json.JSONDecoder().decode(form.decode('utf-8'))
        except Exception as e:
            self._send_error(handler, _('Error: Invalid JSON data sent.'))

        try:
            self.taiga.handle_payload(payload)
        except Exception as e:
            self._send_error(handler, _('Error: Invalid data sent.'))

        # Return OK
        self._send_ok(handler)


class Taiga(callbacks.Plugin):
    """Plugin for communication and notifications of a Taiga project management tool instance"""
    threaded = True

    def __init__(self, irc):
        global instance
        self.__parent = super(Taiga, self)
        self.__parent.__init__(irc)
        instance = self

        callback = TaigaWebHookService(self, irc)
        httpserver.hook('taiga', callback)

    def die(self):
        httpserver.unhook('taiga')

        self.__parent.die()

    def _load_projects(self, channel):
        projects_string = self.registryValue('projects', channel)
        if projects_string is None or len(projects_string) == 0:
            return {}
        else:
            return json.loads(projects_string)

    def _save_projects(self, projects, channel):
        string = ''
        if projects is not None:
            string = json.dumps(projects)
        self.setRegistryValue('projects', value=string, channel=channel)

    def _check_capability(self, irc, msg):
        if ircdb.checkCapability(msg.prefix, 'admin'):
            return True
        else:
            irc.errorNoCapability('admin')
            return False

    class taiga(callbacks.Commands):
        """Taiga commands"""

        class project(callbacks.Commands):
            """Project commands"""

            @internationalizeDocstring
            def add(self, irc, msg, args, channel, project_id, project_slug, taiga_host):
                """[<channel>] <project-id> <project-slug> <taiga-host>

                Announces the changes of the project with the id <project-id>
                and the slug <project-slug> to <channel>.
                """
                if not instance._check_capability(irc, msg):
                    return

                projects = instance._load_projects(channel)
                if project_id in projects:
                    irc.error(_('This project is already announced to this channel.'))
                    return

                # Save new project mapping
                projects[project_id] = {
                    'slug': project_slug,
                    'url': taiga_host + '/project/' + project_slug
                }
                instance._save_projects(projects, channel)

                irc.replySuccess()

            add = wrap(add, ['channel', 'id', 'somethingWithoutSpaces', 'httpUrl'])

            @internationalizeDocstring
            def remove(self, irc, msg, args, channel, project_id):
                """[<channel>] <project-id>

                Stops announcing the changes of the project id <project-id> to
                <channel>.
                """
                if not instance._check_capability(irc, msg):
                    return

                projects = instance._load_projects(channel)
                if project_id not in projects:
                    irc.error(_('This project is not registered to this channel.'))
                    return

                # Remove project mapping
                del projects[project_id]
                instance._save_projects(projects, channel)

                irc.replySuccess()

            remove = wrap(remove, ['channel', 'somethingWithoutSpaces'])

            @internationalizeDocstring
            def list(self, irc, msg, args, channel):
                """[<channel>]

                Lists the registered projects in <channel>.
                """
                if not instance._check_capability(irc, msg):
                    return

                projects = instance._load_projects(channel)
                if projects is None or len(projects) == 0:
                    irc.error(_('This channel has no registered projects.'))
                    return

                for project_id, project_data in projects.items():
                    irc.reply("%s: %s (%s)" % (project_id, project_data['slug'], project_data['url']))

            list = wrap(list, ['channel'])


Class = Taiga


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
