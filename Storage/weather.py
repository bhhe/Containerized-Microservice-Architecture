from sqlalchemy import Column, Integer, String, DateTime, Numeric
from base import Base
import datetime


class Weather(Base):
    """ Blood Pressure """

    __tablename__ = "weather"

    id = Column(Integer, primary_key=True)
    plot_id = Column(String(250), nullable=False)
    tracker_id = Column(String(250), nullable=False)
    relative_humidity = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    low = Column(Numeric, nullable=False)
    high = Column(Numeric, nullable=False)
    avg = Column(Numeric, nullable=False)
    notation = Column(String(50),nullable=False)

    def __init__(self, plot_id, tracker_id, relative_humidity, timestamp, low, high, avg, notation):
        """ Initializes a weather reading """
        self.plot_id = plot_id
        self.tracker_id = tracker_id
        self.relative_humidity = relative_humidity
        self.timestamp = timestamp
        self.low = low
        self.high = high
        self.avg = avg
        self.notation = notation
        self.date_created = datetime.datetime.now()  # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of a weather reading """
        dict = {}
        dict['id'] = self.id
        dict['plot_id'] = self.plot_id
        dict['tracker_id'] = self.tracker_id
        dict['relative_humidity'] = self.relative_humidity
        dict['temperature_range'] = {}
        dict['temperature_range']['low'] = self.low
        dict['temperature_range']['high'] = self.high
        dict['temperature_range']['avg'] = self.avg
        dict['temperature_range']['notation'] = self.notation
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
