# Service Based Architectures
# Receiver
# Bowen He

import connexion
import requests
import yaml
import logging
import datetime
import json
import os
import time
from pykafka import KafkaClient
from logging import config
from connexion import NoContent

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

attempt = 0
while attempt < app_config['kafka']['attempts']:
    logger.info("Attempting to Connect to Kafka #%d" % attempt)
    try:
        client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
        topic = client.topics[str.encode(app_config['events']['topic'])]
        logger.info("Successfully connected to Kafka")
        break
    except Exception as ex:
        error_string = str(ex)
        logger.error("Failed to Connect #%d: %s" % (attempt, error_string))
    attempt += 1
    time.sleep(3)

def request_kafka(reading, event_type):
    producer = topic.get_sync_producer()
    event_id = reading["plot_id"] + reading["tracker_id"] + reading["timestamp"]
    logger.info(f"Received event {event_type} post request with a unique id of {event_id}")
    logger.info(f"Returned event {event_type} post response {event_id} with status 201")
    reading['event_id'] = event_id
    msg = {"type": event_type,
           "datetime":
               datetime.datetime.now().strftime(
                   "%Y-%m-%dT%H:%M:%S"),
           "payload": reading}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode("utf-8"))


def report_weather_reading(body):
    request_kafka(body, "weather")

    return NoContent, 201


def report_soil_reading(body):
    request_kafka(body, "soil")

    return NoContent, 201


def get_weather_readings(timestamp):
    """ Gets new weather readings after the timestamp """
    result = requests.get(app_config["weather"]["url"], params={"timestamp": timestamp})

    return result.json(), result.status_code


def get_soil_readings(timestamp):
    result = requests.get(app_config["soil"]["url"], params={"timestamp": timestamp})

    return result.json(), result.status_code


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("farming_api.yml", base_path="/receiver", strict_validation=True, validate_responses=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(port=8080)
