class Bot:
    def __init__(self, bot_data):
        self.id = bot_data.get('id')
        self.name = bot_data.get('name')
        self.avatar = bot_data.get('avatar')
        self.engine = bot_data.get('engine')
        self.model = bot_data.get('model')
        self.api_key = bot_data.get('api_key')
        self.api_endpoint = bot_data.get('api_endpoint')
        self.system_prompt = bot_data.get('system_prompt')
        self.enable = bot_data.get('enable', True)
        self.temperature = bot_data.get('temperature', 1.0)
        self.history = []

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'avatar': self.avatar,
            'engine': self.engine,
            'model': self.model,
            'api_key': self.api_key,
            'api_endpoint': self.api_endpoint,
            'system_prompt': self.system_prompt,
            'enable': self.enable,
            'temperature': self.temperature
        }

    def add_message_to_history(self, role, content):
        self.history.append({"role": role, "content": content})

    def get_current_history(self):
        return self.history

    def clear_history(self):
        self.history = []

    def update(self, new_data):
        for key, value in new_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
