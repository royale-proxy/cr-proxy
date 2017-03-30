import os
import logging
from glob import glob
from coc.proxyconfig import ProxyConfig

class Replay:
    message_index_file = "message.index"
    message_index = 1

    def __init__(self):
        Replay.start()

    @staticmethod
    def start():
        if ProxyConfig.get_replay_directory() and not os.path.exists(ProxyConfig.get_replay_directory()):
            os.makedirs(ProxyConfig.get_replay_directory())
        Replay.read_message_index()

    @staticmethod
    def read_message_index():
        if not ProxyConfig.get_replay_directory():
            return
        Replay.message_index_filepath = "{}/{}".format(ProxyConfig.get_replay_directory(), Replay.message_index_file)
        if not os.path.exists(Replay.message_index_filepath):
            return
        with open(Replay.message_index_filepath, 'r') as fh:
            index = fh.read()
            Replay.message_index = int(index)

    @staticmethod
    def save_message_index():
        if not ProxyConfig.get_replay_directory():
            return
        if not os.path.exists(ProxyConfig.get_replay_directory()):
            return
        target = open("{}/{}".format(ProxyConfig.get_replay_directory(), Replay.message_index_file), 'w')
        target.write(str(Replay.message_index))
        target.close()

    @staticmethod
    def get_next_message_index():
        current = Replay.message_index
        Replay.message_index += 1
        return current

    @staticmethod
    def save(messageid, version, payload):
        if not ProxyConfig.get_replay_directory():
            return
        if not os.path.exists(ProxyConfig.get_replay_directory()):
            os.makedirs(ProxyConfig.get_replay_directory())

        target = open("{}/{}-{}.{}".format(ProxyConfig.get_replay_directory(), str(Replay.get_next_message_index()).zfill(4), str(messageid), "bin"), "wb")
        target.write(messageid.to_bytes(2, byteorder="big"))
        target.write(len(payload).to_bytes(3, byteorder="big"))
        target.write(version.to_bytes(2, byteorder="big"))
        target.write(payload)
        target.close()
        Replay.save_message_index()

    @staticmethod
    def read(message_index):
        if not ProxyConfig.get_replay_directory():
            return
        glob_string = "{}/{}-*".format(ProxyConfig.get_replay_directory(), str(Replay.message_index).zfill(4))
        files = glob(glob_string)
        if len(files) != 1:
            return

        file_path = files[0]
        with open(file_path, 'rb') as fh:
            message = fh.read()
        return message
