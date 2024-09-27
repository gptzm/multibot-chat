from .bot import Bot

class BotManager:
    def __init__(self, username):
        self.username = username
        self.bots = []
        self.chat_config = {}
        self.history_versions = []
        self.current_history_version = 0
        self.group_history_versions = []
        self.current_group_history_version = 0

    def add_bot(self, bot_data):
        new_bot = Bot(bot_data)
        self.bots.append(new_bot)

    def update_bot(self, bot_id, new_data):
        bot = self.get_bot_by_id(bot_id)
        if bot:
            bot.update(new_data)

    def delete_bot(self, bot_id):
        self.bots = [bot for bot in self.bots if bot.id != bot_id]

    def get_bot_by_id(self, bot_id):
        return next((bot for bot in self.bots if bot.id == bot_id), None)

    def get_current_history_by_bot(self, bot):
        return bot.get_current_history()

    def add_message_to_history(self, bot_id, message):
        bot = self.get_bot_by_id(bot_id)
        if bot:
            bot.add_message_to_history(message['role'], message['content'])

    def create_new_history_version(self):
        for bot in self.bots:
            bot.clear_history()
        self.current_history_version += 1
        # 添加新的历史版本逻辑...

    def get_chat_config(self):
        return self.chat_config

    def update_chat_config(self, new_config):
        self.chat_config.update(new_config)

    # 其他方法...
