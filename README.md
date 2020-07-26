# default-discord-bot

![Python](https://img.shields.io/badge/python-3.7%20%7C%203.8-blue)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux-lightgrey)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Paprikar/default-discord-bot.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Paprikar/default-discord-bot/context:python)
[![GitHub License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Discord bot aimed at working with media content written on Python.

- [Installation](#installation)
  - [Dependencies installation](#dependencies-installation)
  - [Additional dependencies installation](#additional-dependencies-installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Advanced](#advanced)
- [Modules](#modules)
- [Commands](#commands)

---

## Installation

Requires Python 3.7 or never.

### Dependencies installation

```
pip install aiofiles==0.5.0 aiohttp==3.6.2 discord.py==1.3.4
```
or
```
pip install -r requirements.txt
```

### Additional dependencies installation

#### PostgreSQL

For more stable bot operation the PostgreSQL database adapter is used.

```
pip install psycopg2==2.8.5
```

## Configuration

The configuration of the bot is performed by the `JSON` file.

- token `Type: string`

    Bot's token.

- command_prefix `Type: string` `Optional`

    The line from which the message should begin for the bot to react in a special discord text channel.

    Default value is `"!"`.

- bot_channel_id `Type: number`

    The discord text channel ID in which the bot reacts to commands.

- db `Type: object` `Optional`

    The section of parameters responsible for database configuration.

    Default value is `null`.

    - dbname `Type: string`

        The database name.

    - user `Type: string` `Optional`

        User name used to authenticate.

        Default value is `"postgres"`.

    - password `Type: string` `Optional`

        Password used to authenticate.

        Default value is `null`.

    - host `Type: string` `Optional`

        Database host address.

        Defaults to UNIX socket.

    - port `Type: string or number` `Optional`

        Connection port number.

        Default value is `5432`.

- pics_categories `Type: object` `Optional`

    The section of parameters responsible for image categories configuration.

    Accepts JSON object with keys which are names of categories and values of object type which are parameters for corresponding categories.

    Category parameters linked to the module may be necessary or optional for the corresponding module.
    If you specify at least one parameter for the module, all parameters that are mandatory for the corresponding module become mandatory parameters for the current category.

    Categories have the following configuration parameters:

    - send_directory `Type: string`

        Relates to the `PicsSendingModule`.

        The directory whose files are used for sending.

    - send_channel_id `Type: number`

        Relates to the `PicsSendingModule`.

        The discord text channel ID into which messages are sent.

    - send_start `Type: string`

        Relates to the `PicsSendingModule`.

        Time to start sending messages in "HH:MM" format.
        Where `HH` is an hour (24-hour clock) as a zero-padded decimal number and `MM` is a minute as a zero-padded decimal number.

    - send_end `Type: string`

        Relates to the `PicsSendingModule`.

        Time to end sending messages in "HH:MM" format.
        Where `HH` is an hour (24-hour clock) as a zero-padded decimal number and `MM` is a minute as a zero-padded decimal number.

    - send_reserve_days `Type: number`

        Relates to the `PicsSendingModule`.

        The number of days that affect the period of messages sent.
        With this period, images will end after this number of days.

    - send_archive_directory `Type: string` `Optional`

        Relates to the `PicsSendingModule`.

        The directory where the sent images will be moved to instead of being deleted.

    - suggestion_directory `Type: string`

        Relates to the `PicsSuggestionModule`.

        The directory to which images will be saved after approval.

    - suggestion_channel_id `Type: number`

        Relates to the `PicsSuggestionModule`.

        The discord text channel ID into which messages will be sent to prove images attached to them.

    - suggestion_positive `Type: string` `Optional`

        Relates to the `PicsSuggestionModule`.

        Unicode symbol in code point format ("U+XXXX").
        Appears under the message as a reaction to make an approval.

        Default value is `"U+2705"` (✅).

    - suggestion_negative `Type: string` `Optional`

        Relates to the `PicsSuggestionModule`.

        Unicode symbol in code point format ("U+XXXX").
        Appears under the message as a reaction to make a deviation.

        Default value is `"U+274E"` (❎).

- reconnect_timeout `Type: number` `Optional`

    The amount of time in seconds between attempts to reconnect at the start of the bot.

    Default value is `60`.

- logging_level `Type: string or number` `Optional`

    Logging level used to output into console / log file.

    The values [1, 2, 3, 4, 5] do the same as the ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] values respectively.

    Default value is `"INFO"`.

- logging_file `Type: string` `Optional`

    The path to the file that will be used for logging.

    Default value is `"./launch.py.log"`.

## Usage

The bot can be launched through the `launch.py` file.

```
python launch.py
```

This file is able to accept arguments.
For more information, check the help message.

```
python launch.py --help
```

### Advanced

The bot needs the path to the configuration file, the logger object and the formatter object to be launched.

```python
import logging

from bot.utils import init_logger


config = 'config.json'
formatter = logging.Formatter(
    '[%(datetime)s][%(threadName)s][%(name)s]'
    '[%(levelname)s]: %(message)s')
logger = init_logger(__file__, formatter)
```

Then create an object of `DiscordBot` type and execute its `run` method.

```python
from bot import DiscordBot


bot = DiscordBot(config, logger, formatter)
bot.run()
```

The bot is turned off by pressing the interrupt key or by executing the bot's `shutdown` command.

## Modules

The bot uses modules to extend its functionality.

- PicsSendingModule

    A module for sending images to discord text channels.

    Depends on the following configuration parameters:

    - send_directory
    - send_channel_id
    - send_start
    - send_end
    - send_reserve_days
    - send_archive_directory

- PicsSuggestionModule

    A module for processing image suggestions for further saving them to disk.

    Depends on the following configuration parameters:

    - suggestion_directory
    - suggestion_channel_id
    - suggestion_positive
    - suggestion_negative

## Commands

The bot can perform certain actions after typing the corresponding commands.
For the bot to react to commands, a prefix must be provided in front of them.

- ping

    Sends the answer "...pong" to the same text channel.
    Used to check if the bot is online.

- qsize

    Sends a message containing the number of images in the queue for the corresponding categories.

    List the names of the required categories separated by a space to send information about the corresponding categories, otherwise send information about all of them.

- restart

    > The user typing this command must have administrator rights on the corresponding discord server.

    Executes a full bot restart.

    Supplement the command with an additional argument of integer type to specify a timeout for the restart.
    After the timeout expires, the bot will be forcibly restarted.
    Default timeout value is `None`, at which the bot will be launched only after its full shutdown.

- shutdown

    > The user typing this command must have administrator rights on the corresponding discord server.

    Executes a full bot shutdown.

    Supplement the command with an additional argument of integer type to specify a timeout for the shutdown.
    After the timeout expires, the bot will be forcibly shutdown.
    Default timeout value is `None`, at which the bot will wait until it is completely shutdown.

## License

default-discord-bot is licensed using the MIT License, as found in the [LICENSE](LICENSE) file.
