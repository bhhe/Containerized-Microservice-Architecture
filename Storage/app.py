# Service Based Architectures
# Storage
# Bowen He

import connexion
import yaml
import logging
import datetime
import json
import os
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from connexion import NoContent
from logging import config
from sqlalchemy import create_engine
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from base import Base
from weather import Weather
from soil import Soil

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
    datastore = app_config["datastore"]

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

DB_ENGINE = create_engine(f'mysql+pymysql://{datastore["user"]}:{datastore["password"]}@{datastore["hostname"]}:{datastore["port"]}/{datastore["db"]}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def store_reading(body, event_type):
    session = DB_SESSION()
    if event_type == 'weather':
        wr = Weather(body['plot_id'],
                     body['tracker_id'],
                     body['relative_humidity'],
                     body['timestamp'],
                     body['temperature_range']['low'],
                     body['temperature_range']['high'],
                     body['temperature_range']['avg'],
                     body['temperature_range']['notation'])
        session.add(wr)

    elif event_type == 'soil':
        sr = Soil(body['plot_id'],
                  body['tracker_id'],
                  body['ph_level'],
                  body['phosphorus'],
                  body['saturation'],
                  body['timestamp'])
        session.add(sr)

    session.commit()
    session.close()

    logger.debug(f"Stored event {event_type} post request with a unique id of {body['event_id']}")

    return NoContent, 201


def get_weather_readings(start_timestamp, end_timestamp):
    """ Gets new weather readings after the timestamp """
    session = DB_SESSION()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    print(end_timestamp_datetime)
    readings = session.query(Weather).filter(
            and_(Weather.date_created >= start_timestamp_datetime,
                 Weather.data_created < end_timestamp_datetime))
    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()
    logger.info("Query for Weather readings after %s returns %d results" % (timestamp, len(results_list)))

    return results_list, 200


def get_soil_readings(start_timestamp, end_timestamp):
    """ Gets new soil readings after the timestamp """
    session = DB_SESSION()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    print(end_timestamp_datetime)
    readings = session.query(Soil).filter(
            and_(Soil.date_created >= start_timestamp_datetime,
                 Soil.data_created < end_timestamp_datetime))
    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()
    logger.info("Query for Soil readings after %s returns %d results" % (timestamp, len(results_list)))

    return results_list, 200


def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history n the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_groups',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "weather": # Change this to your event type
            logger.info(f"Received Payload {msg['type']} event: {msg['payload']['event_id']}")
            store_reading(payload, "weather")
        elif msg["type"] == "soil":
            logger.info(f"Received Payload {msg['type']} event: {msg['payload']['event_id']}")
            store_reading(payload, "soil")
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("farming_api.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    logger.info(f"Connecting to DB {datastore['hostname']}. Port:{datastore['port']}")
    app.run(port=8090)
