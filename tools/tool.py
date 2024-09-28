import os
import json

class ToolManager:
    def __init__(self):
        self.tools = {}
        self.load_tools()

    def load_tools(self):
        tools_dir = os.path.dirname(os.path.abspath(__file__))
        for folder in os.listdir(tools_dir):
            folder_path = os.path.join(tools_dir, folder)
            if os.path.isdir(folder_path):
                config_path = os.path.join(folder_path, 'config.json')
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    self.tools[folder] = {
                        'path': folder_path,
                        'config': config,
                        'name': config.get('name', folder),
                        'description': config.get('description', ''),
                        'main_file': config.get('main_file', '')
                    }

    def get_tools(self):
        return self.tools

    def get_tool(self, tool_name):
        return self.tools.get(tool_name)

tool_manager = ToolManager()

def get_tools():
    return tool_manager.get_tools()

def get_tool(tool_name):
    return tool_manager.get_tool(tool_name)