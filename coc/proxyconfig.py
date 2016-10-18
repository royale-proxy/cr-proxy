import os
import json
from distutils.command.config import config


class ProxyConfig:
    config = None
    
    def __init__(self, config_file):
        ProxyConfig.start(config_file)
        
    @staticmethod
    def start(config_file):
        with open(config_file, 'r') as fh:
            ProxyConfig.config = json.load(fh)
        
    @staticmethod
    def get_replay_directory():
        if ProxyConfig.config and 'replayDirectory' in ProxyConfig.config:
            return ProxyConfig.config['replayDirectory'];
        return None