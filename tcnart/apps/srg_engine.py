import logging
import zenoh
from tcnart.network.sis_subscriber import start_sis_join_subscriber
logging.basicConfig(level=logging.DEBUG)

zenoh_config = "/Users/ecku/mydev/artekmed/zenoh_client_config/ueck_localrouter/zenoh_config.json5"
topic_prefix = "tcn/loc/pcpd"

sis_join_topic = f"{topic_prefix}/*/sis/join"

zenoh.init_log_from_env_or("warn")
session = zenoh.open(zenoh.Config.from_json5(open(zenoh_config).read()))

class DbgHelper:
    def __init__(self, name):
        self.stream_name = name
    def __call__(self, args):
        topic, msg = args
        print(f"received message {topic} {msg}")

dbg_helper = DbgHelper("dbg")

thread = start_sis_join_subscriber(None, dbg_helper, session, sis_join_topic)

thread.join()