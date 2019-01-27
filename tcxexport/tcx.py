import random
from datetime import datetime, timedelta
from uuid import uuid4
from xml.etree import ElementTree
from xml.etree.cElementTree import Element


class Trackpoint(object):
    def __init__(self, timestamp: datetime):
        self.timestamp = timestamp
        self.altitude = None
        self.long = None
        self.lat = None

    def set_position(self, long: float, lat: float):
        self.long = long
        self.lat = lat

    def set_altitude(self, altitude: float):
        self.altitude = altitude

    def get_xml(self):
        """
        <Trackpoint>
            <Time>2019-01-25T18:34:05Z</Time>
            <Position>
              <LatitudeDegrees>51.026771</LatitudeDegrees>
              <LongitudeDegrees>13.819436</LongitudeDegrees>
            </Position>
            <HeartRateBpm>
              <Value>168</Value>
            </HeartRateBpm>
            <AltitudeMeters>104</AltitudeMeters>
            <Extensions>
              <TPX xmlns="http://www.garmin.com/xmlschemas/ActivityExtension/v2">
                <Speed>0</Speed>
              </TPX>
            </Extensions>
          </Trackpoint>
        """
        trackpoint = Element('Trackpoint')

        time = Element('Time')
        time.text = self.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        trackpoint.append(time)

        if self.altitude is not None:
            altitude_meters = Element('AltitudeMeters')
            altitude_meters.text = str(self.altitude)
            trackpoint.append(altitude_meters)

        if self.lat is not None and self.long is not None:
            position = Element('Position')
            trackpoint.append(position)

            latitude_degrees = Element('LatitudeDegrees')
            latitude_degrees.text = str(self.lat)
            position.append(latitude_degrees)

            longitude_degrees = Element('LongitudeDegrees')
            longitude_degrees.text = str(self.long)
            position.append(longitude_degrees)

        return trackpoint


class Track(object):
    def __init__(self):
        self.trackpoints = []

    def add_trackpoint(self, trackpoint: Trackpoint):
        self.trackpoints.append(trackpoint)

    def get_xml(self):
        track = Element('Track')

        for trackpoint in self.trackpoints:
            track.append(trackpoint.get_xml())

        return track


class Lap(object):
    def __init__(self):
        self.track = None

    def get_xml(self):
        lap = Element('Lap')
        lap.append(self.track.get_xml())

        return lap


class Activity(object):
    def __init__(self):
        self.laps = []
        self.id = uuid4()

    def add_lap(self, lap: Lap):
        self.laps.append(lap)

    def get_xml(self):
        activity = Element('Activity')

        id_ = Element('Id')
        id_.text = str(self.id)
        activity.append(id_)

        for lap in self.laps:
            activity.append(lap.get_xml())

        return activity


class TCXData(object):
    def __init__(self):
        self.activities = []

    def add_activity(self, activity: Activity):
        self.activities.append(activity)

    def get_xml(self):
        training_center_db = Element(
            'TrainingCenterDatabase',
            attrib={
                'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema',
                'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                'xmlns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'})

        activities = Element('Activities')
        training_center_db.append(activities)

        for activity in self.activities:
            activities.append(activity.get_xml())

        tree = ElementTree.ElementTree(training_center_db)

        return tree

    def write(self, out_file_path: str):
        tree = self.get_xml()
        tree.write(out_file_path)
