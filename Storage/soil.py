from sqlalchemy import Column, Integer, String, DateTime, Numeric
from base import Base
import datetime


class Soil(Base):
    """ Blood Pressure """

    __tablename__ = "soil"

    id = Column(Integer, primary_key=True)
    plot_id = Column(String(250), nullable=False)
    tracker_id = Column(String(250), nullable=False)
    ph_level = Column(Integer, nullable=False)
    phosphorus = Column(Integer, nullable=False)
    saturation = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, plot_id, tracker_id, ph_level, phosphorus, saturation, timestamp):
        """ Initializes a soil reading """
        self.plot_id = plot_id
        self.tracker_id = tracker_id
        self.ph_level = ph_level
        self.phosphorus = phosphorus
        self.saturation = saturation
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now()  # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of a soil reading """
        dict = {}
        dict['id'] = self.id
        dict['plot_id'] = self.plot_id
        dict['tracker_id'] = self.tracker_id
        dict['ph_level'] = self.ph_level
        dict['phosphorus'] = self.phosphorus
        dict['saturation'] = self.saturation
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
