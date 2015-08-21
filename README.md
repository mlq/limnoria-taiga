# limnoria-taiga

limnoria-taiga is a plugin for [limnoria](https://github.com/ProgVal/Limnoria) that provides support for [taiga](https://taiga.io) webhook notifications. Currently it has the following features:

  - Support of different payload types (milestone, user story, task, issue, wikipage and test)
  - Support of webhook signature verification (Option to set the shared key and to disable the verification)
  - Commands to manage subscribed projects per channel
  - Localization

### Installation

To install this plugin just copy its directory to the `supybot.directories.plugins` directory of your limnoria instance and enable it in your configuration file under `supybot.plugins`. For more information checkout the [Supybot user guide](http://doc.supybot.aperio.fr/en/latest/use/index.html).

### Configuration

The _limnoria-taiga_ plugin uses the build-in web service of Limnoria therefore it listens on the address configured by `supybot.servers.http.hosts[4,6]` and `supybot.servers.http.port`. For more information on the HTTP server of Limnoria checkout the '[Using the HTTP server](http://doc.supybot.aperio.fr/en/latest/use/httpserver.html)' chapter of their documentation.

Depending on the configuration of your Limnoria instance and your web server the plugin now listens on the following address where it accepts the network and the channel as a parameter:

`http://<host>:<port>/taiga/<network>/<channel>`

The placeholders are defined as followed:

  - `<host>` - The host defined by the external IP of the service
  - `<port>` - The port that the HTTP server of Limnoria listens to
  - `<network>` - The network that the Limnoria instance is connected to
  - `<channel>` - The channel that the Limnoria instance is in

For instance if your bot is in the _OFTC_ network and in the _#limnoria-taiga_ channel, the plugin listens on the following URL for webhook notifications:

`http://limnoria.taiga.io:8080/taiga/OFTC/limnoria-taiga`

Now you need to add this address as a new webhook in the project settings of your Taiga instance. Therefore you go to `Settings -> Integrations -> Webhooks` and click `Add a new webhook`. Under `Type the service payload` you enter the previously created address. Under `Type the service secret` you should come up with a random passphrase that is not easily discovered and will be shared between your Taiga installation and your Limnoria bot. This secret is used to verify the signatures that are attached to the notifications sent by Taiga. Then you need to set the secret as a configuration option of the channel in that you are using the bot as the `plugins.Taiga.secret-key` option. If you do not want to use signature verification you can set `plugins.Taiga.verify-signature` to `False`.

### Commands

- `taiga project add [<channel>] <project-id> <project-slug> <project-host>` -
  This command subscribes a new project to the channel:
    - `[<channel>]` - The channel that should be used. _(Optional, defaults to the current channel)_
    - `<project-id>` - The id of the Taiga project
    - `<project-slug>` - The slug of the Taiga project
    - `<project-host>` - The host of the Taiga project

  Example: To subscribe the _example_project_ to the current channel you can run the following command: `taiga project add 1 example_project https://taiga.example.com`

- `taiga project remove [<channel>] <project-slug>` - This command removes a subscribed project from the channel:
    - `[<channel>]` - The channel that should be used. _(Optional, defaults to the current channel)_
    - `<project-slug` - The slug of the Taiga project

- `taiga project list [<channel>]` - Lists the subscribed projects from the channel:
    - `[<channel>]` - The channel that should be used. _(Optional, defaults to the current channel)_

### Options

The following options can be set for each channel and are used to configure the signature verification of the plugin and the subscribed projects (this option should only be set by the commands of this plugin).

- `plugins.Taiga.secret-key` - Defines the secret key that is shared between the bot and the Taiga instance _(Default: XXXXXXXX)_
- `plugins.Taiga.verify-signature` - Defines if the signatures of recieved notifications should be verified or not _(Default: True)_
- `plugins.Taiga.projects` - Saves the subscribed project mappings _(Default: empty)_ **Readonly!**

In addition all the formats that are used to notify the channel about changes on the Taiga project can be configured:

- `plugins.Taiga.format.milestone-created` - The format that is used if a milestone has been created
- `plugins.Taiga.format.milestone-deleted` - The format that is used if a milestone has been deleted
- `plugins.Taiga.format.milestone-changed` - The format that is used if a milestone has been changed
- `plugins.Taiga.format.userstory-created` - The format that is used if an userstory has been created
- `plugins.Taiga.format.userstory-deleted` - The format that is used if an userstory has been deleted
- `plugins.Taiga.format.userstory-changed` - The format that is used if an userstory has been changed
- `plugins.Taiga.format.task-created` - The format that is used if a task has been created
- `plugins.Taiga.format.task-deleted` - The format that is used if a task has been deleted
- `plugins.Taiga.format.task-changed` - The format that is used if a task has been changed
- `plugins.Taiga.format.issue-created` - The format that is used if an issue has been created
- `plugins.Taiga.format.issue-deleted` - The format that is used if an issue has been deleted
- `plugins.Taiga.format.issue-changed` - The format that is used if an issue has been changed
- `plugins.Taiga.format.wikipage-created` - The format that is used if a wikipage has been created
- `plugins.Taiga.format.wikipage-deleted` - The format that is used if a wikipage has been deleted
- `plugins.Taiga.format.wikipage-changed` - The format that is used if a wikipage changed

For those formats you can pass different arguments that contain the values of the notification. The default values are:

- `milestone/userstory/task/issue/wikipage` - The data of the payload as described [here](http://taigaio.github.io/taiga-doc/dist/webhooks.html#_test_payload)
- `project` - The project containing the *name* and the *id* of the project
- `user` - The user containing the *name* and the *id* of it that executed the action described by this event.
- `url` - The direct url to the data described by this notification 
- `change` - The different changes (Only set iff a *changed* event occured)

As an example the format of the `plugins.Taiga.format.milestone-created` notifcation could be defined as `[{project[name]}] Milestone #{milestone[id]} {milestone[name]} created by {user[name]}`.

### F.A.Q.

**My bot does not recieve any webhook notifications, what could be wrong?**

Make sure that you have set `WEBHOOKS_ENABLED = True` in your `./taiga-back/settings/local.py` configuration file of your Taiga instance.
