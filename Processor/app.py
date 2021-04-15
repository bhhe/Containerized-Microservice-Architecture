# Service Based Architectures
# Processor
# Bowen He

import connexion
import yaml
import logging
import datetime
import json
import requests
import os

from connexion import NoContent
from logging import config
from apscheduler.schedulers.background import BackgroundScheduler
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

def get_stats():
    """ Gets new soil readings after the timestamp """
    logger.info("Get Stats request has started")
    if os.path.exists(app_config["datastore"]["filename"]):
        with open(app_config["datastore"]["filename"]) as data_json:
            stat_logs = json.load(data_json)
        logger.debug(stat_logs)
    else:
        logger.error("Statistics do not exist")
        return NoContent, 404
    logger.info("Get Statistics Request completed")

    return stat_logs, 200


def populate_stats():
    """ Periodically update stats """
    logger.info("Periodic Processing Started")
    data_json = read_json()
    current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    if data_json["last_updated"] > current_time:
        return
    data_json['current_timestamp'] = current_time
    update_weather(data_json)
    update_soil(data_json)
    data_json['last_updated'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    write_json(data_json)
    logger.debug(data_json)
    logger.info("Period Processing has ended")


def read_json():
    if os.path.exists(app_config["datastore"]["filename"]):
        with open(app_config["datastore"]["filename"]) as data_json:
            stat_logs = json.load(data_json)
        print("Data Json Exist")
    else:
        print("Data Json not exist")
        stat_logs = app_config['default_stats']
    return stat_logs


def write_json(data_json):
    with open(app_config['datastore']['filename'], 'w') as outfile:
        json.dump(data_json, outfile, indent=4, sort_keys=True)


def update_weather(data_json):
    weather_result = requests.get(app_config["weather"]["url"], 
                                  params={
                                      "start_timestamp": data_json["last_updated"],
                                      "end_timestamp": data_json["current_timestamp"]
                                  })
    if weather_result.status_code == 200:
        weather_list = weather_result.json()
        logger.info("Received %d from Weather" % len(weather_list))
        for reading in weather_list:
            data_json['num_weather_readings'] += 1
            if reading['temperature_range']['avg'] > data_json['max_weather_temp_avg']:
                data_json['max_weather_temp_avg'] = reading['temperature_range']['avg']
            if reading['temperature_range']['high'] > data_json['max_weather_temp_high']:
                data_json['max_weather_temp_high'] = reading['temperature_range']['high']
            if reading['temperature_range']['low'] > data_json['max_weather_temp_low']:
                data_json['max_weather_temp_low'] = reading['temperature_range']['low']
            if reading['relative_humidity'] > data_json['max_weather_relative_humidity']:
                data_json['max_weather_relative_humidity'] = reading['relative_humidity']
    else:
        logger.error("Did not receive 200 response from Weather")


def update_soil(data_json):
    soil_result = requests.get(app_config["soil"]["url"],
                               params={
                                   "start_timestamp": data_json["last_updated"],
                                   "end_timestamp": data_json["current_timestamp"]
                               })
    if soil_result.status_code == 200:
        soil_list = soil_result.json()
        logger.info("Received %d from Soil" % len(soil_list))
        for reading in soil_list:
            data_json['num_soil_readings'] += 1
            if reading['ph_level'] > data_json['max_soil_ph_reading']:
                data_json['max_soil_ph_reading'] = reading['ph_level']
            if reading['phosphorus'] > data_json['max_soil_phosphorus_reading']:
                data_json['max_soil_phosphorus_reading'] = reading['phosphorus']
            if reading['saturation'] > data_json['max_soil_saturation_reading']:
                data_json['max_soil_saturation_reading'] = reading['saturation']
    else:
        logger.error("Did not receive 200 response from Soil")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("farming_api.yml", base_path="/processor", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)
