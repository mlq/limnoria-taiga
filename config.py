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

import supybot.conf as conf
import supybot.registry as registry
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Taiga')
except:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified themself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Taiga', True)


Taiga = conf.registerPlugin('Taiga')

# Settings
conf.registerChannelValue(Taiga, 'projects',
    registry.Json({}, _("""List of projects""")))

conf.registerChannelValue(Taiga, 'secret-key',
    registry.String("XXXXXXXX", _("""The service secret key""")))

conf.registerChannelValue(Taiga, 'verify-signature',
    registry.Boolean(True, _("""Whether the signature should be checked or not""")))

# Format
conf.registerGroup(Taiga, 'format')

conf.registerChannelValue(Taiga.format, 'milestone-created',
    registry.String(_("""\x02[{project[name]}]\x02 Milestone \x02#{milestone[id]} {milestone[name]}\x02 created by {user[name]} {url}"""),
                    _("""Format for milestone/create events.""")))
conf.registerChannelValue(Taiga.format, 'milestone-deleted',
    registry.String(_("""\x02[{project[name]}]\x02 Milestone \x02#{milestone[id]} {milestone[name]}\x02 deleted by {user[name]} {url}"""),
                    _("""Format for milestone/delete events.""")))
conf.registerChannelValue(Taiga.format, 'milestone-changed',
    registry.String(_("""\x02[{project[name]}]\x02 Milestone \x02#{milestone[id]} {milestone[name]}\x02 changed by {user[name]} {url}"""),
                    _("""Format for milestone/change events.""")))

conf.registerChannelValue(Taiga.format, 'userstory-created',
    registry.String(_("""\x02[{project[name]}]\x02 Userstory \x02#{userstory[id]} {userstory[subject]}\x02 created by {user[name]} {url}"""),
                    _("""Format for userstory/create events.""")))
conf.registerChannelValue(Taiga.format, 'userstory-deleted',
    registry.String(_("""\x02[{project[name]}]\x02 Userstory \x02#{userstory[id]} {userstory[subject]}\x02 deleted by {user[name]} {url}"""),
                    _("""Format for userstory/delete events.""")))
conf.registerChannelValue(Taiga.format, 'userstory-changed',
    registry.String(_("""\x02[{project[name]}]\x02 Userstory \x02#{userstory[id]} {userstory[subject]}\x02 changed by {user[name]} {url}"""),
                    _("""Format for userstory/change events.""")))

conf.registerChannelValue(Taiga.format, 'task-created',
    registry.String(_("""\x02[{project[name]}]\x02 Task \x02#{task[id]} {task[subject]}\x02 created by {user[name]} {url}"""),
                    _("""Format for task/create events.""")))
conf.registerChannelValue(Taiga.format, 'task-deleted',
    registry.String(_("""\x02[{project[name]}]\x02 Task \x02#{task[id]} {task[subject]}\x02 deleted by {user[name]} {url}"""),
                    _("""Format for task/delete events.""")))
conf.registerChannelValue(Taiga.format, 'task-changed',
    registry.String(_("""\x02[{project[name]}]\x02 Task \x02#{task[id]} {task[subject]}\x02 changed by {user[name]} {url}"""),
                    _("""Format for task/change events.""")))

conf.registerChannelValue(Taiga.format, 'issue-created',
    registry.String(_("""\x02[{project[name]}]\x02 Issue \x02#{issue[id]} {issue[subject]}\x02 created by {user[name]} {url}"""),
                    _("""Format for issue/create events.""")))
conf.registerChannelValue(Taiga.format, 'issue-deleted',
    registry.String(_("""\x02[{project[name]}]\x02 Issue \x02#{issue[id]} {issue[subject]}\x02 deleted by {user[name]} {url}"""),
                    _("""Format for issue/delete events.""")))
conf.registerChannelValue(Taiga.format, 'issue-changed',
    registry.String(_("""\x02[{project[name]}]\x02 Issue \x02#{issue[id]} {issue[subject]}\x02 changed by {user[name]} {url}"""),
                    _("""Format for issue/change events.""")))

conf.registerChannelValue(Taiga.format, 'wikipage-created',
    registry.String(_("""\x02[{project[name]}]\x02 Wikipage \x02#{wikipage[slug]} {wikipage[name]}\x02 created by {user[name]} {url}"""),
                    _("""Format for wikipage/create events.""")))
conf.registerChannelValue(Taiga.format, 'wikipage-deleted',
    registry.String(_("""\x02[{project[name]}]\x02 Wikipage \x02#{wikipage[slug]} {wikipage[name]}\x02 deleted by {user[name]} {url}"""),
                    _("""Format for wikipage/delete events.""")))
conf.registerChannelValue(Taiga.format, 'wikipage-changed',
    registry.String(_("""\x02[{project[name]}]\x02 Wikipage \x02#{wikipage[slug]} {wikipage[name]}\x02 changed by {user[name]} {url}"""),
                    _("""Format for wikipage/change events.""")))

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
