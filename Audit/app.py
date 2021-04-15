# Service Based Architectures
# Audit
# Bowen He

import connexion
import yaml
import logging
import json
import os
from pykafka import KafkaClient
from logging import config
from flask_cors import CORS, cross_origin

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

def get_reading(index, event_type):
    """" Get event_type Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)

    logger.info(f"Retrieving {event_type} at index %d" % index)
    try:
        event_list = []
        found = -1
        for msg in consumer:
            msg_str = msg.value.decode("utf-8")
            msg = json.loads(msg_str)
            if msg['type'] == event_type:
                event_list.append(msg)
            if (index - len(event_list)) == found:
                logger.info(f"Message {event_type} found for index {index}")
                return event_list[index], 200

    except:
        logger.error("No more messages found")

    logger.error(f"Could not find {event_type} at index {index}")

    return {"message": "Not Found"}, 404


def get_weather_readings(index):
    return get_reading(index, "weather")


def get_soil_readings(index):
    return get_reading(index, "soil")

app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

app.add_api("farming_api.yml", base_path="/audit", strict_validation=True, validate_responses=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(port=8110)
