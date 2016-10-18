import sys
import glob
import os
from twisted.internet import reactor
from coc.message.definitions import CoCMessageDefinitions
from coc.server.endpoint import CoCServerEndpoint
from coc.server.factory import CoCServerFactory
from coc.client.endpoint import CoCClientEndpoint
from coc.proxyconfig import ProxyConfig
from coc.message.decoder import CoCMessageDecoder
from coc.replay import Replay

config_file = "config.json"

def get_filepath_by_message_index(message_index):
    if not ProxyConfig.get_replay_directory():
        return None
    glob_string = "{}/{}-*.bin".format(ProxyConfig.get_replay_directory(), str(message_index).zfill(4))
    matches = glob.glob(glob_string)
    if len(matches) == 1:
        return matches[0]
    return None

def start():
    ProxyConfig.start(config_file)
    Replay.start()
  
if __name__ == "__main__":
    start()
    
    
    message_index = sys.argv[1]
    filepath = get_filepath_by_message_index(message_index)

    print ("found message {}".format(filepath))
    
    definitions = CoCMessageDefinitions.read()
    decoder = CoCMessageDecoder(definitions)
    decoded = decoder.decodeFile(filepath)
    decoder.dump(decoded)