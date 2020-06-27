class DiscordBotContainer:

    def __init__(self):
        self.client = None
        self.logger = None
        self.token = None
        self.command_prefix = None
        self.bot_channel_id = None
        self.pics_categories = None
        self.discord_bot = None
        self.shutdown_allowed = False
