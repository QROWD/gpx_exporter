import math
from argparse import ArgumentParser
from datetime import datetime

from cassandra.cluster import Cluster

import tcx


def parse_timestamp(timestamp_str: str):
    return datetime.strptime(timestamp_str, '%Y%m%d%H%M%S%f')


def get_magnitude(x, y, z):
    return math.sqrt(x**2 + y**2 + z**2)


def main(db_host, db_port, db_login, user, date_str, out_file_path):
    data = {}

    cluster = Cluster([db_host], port=db_port, cql_version='3.4.4')
    session = cluster.connect(user)

    print(f'Getting accelerometer information for user {user} on day '
          f'{date_str}')
    res = session.execute(
        f'SELECT'
        f'  timestamp, x, y, z '
        f'FROM '
        f'  {user}.accelerometerevent '
        f'WHERE '
        f'  day=\'{date_str}\'')

    for row in res:
        timestamp = parse_timestamp(row.timestamp)

        if data.get(timestamp) is None:
            data[timestamp] = {}

        magnitude = get_magnitude(row.x, row.y, row.z)
        data[timestamp]['acc'] = magnitude

    print(f'Getting GPS information for user {user} on day {date_str}')
    res = session.execute(
        f'SELECT'
        f'  timestamp, point '
        f'FROM '
        f'  {user}.locationeventpertime '
        f'WHERE '
        f'  day=\'{date_str}\' LIMIT 100')

    for row in res:
        timestamp = parse_timestamp(row.timestamp)

        if data.get(timestamp) is None:
            data[timestamp] = {}

        lat = row.point.latitude
        lon = row.point.longitude
        data[timestamp]['lat'] = lat
        data[timestamp]['lon'] = lon

    tcx_track = tcx.Track()

    for timestamp, entry in data.items():
        tcx_trackpoint = tcx.Trackpoint(timestamp)
        if entry.get('acc') is not None:
            tcx_trackpoint.set_altitude(entry['acc'])

        if entry.get('lat') is not None:
            tcx_trackpoint.set_position(entry['lon'], entry['lat'])

        tcx_track.add_trackpoint(tcx_trackpoint)

    tcx_lap = tcx.Lap()
    tcx_lap.track = tcx_track
    tcx_activity = tcx.Activity()
    tcx_activity.add_lap(tcx_lap)
    tcx_data = tcx.TCXData()
    tcx_data.add_activity(tcx_activity)
    tcx_data.write(out_file_path)


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('dbhost')
    argparser.add_argument('dbport', type=int)
    argparser.add_argument('dbuser')
    argparser.add_argument('user')
    argparser.add_argument('date')
    argparser.add_argument('outfile')

    rgs = argparser.parse_args()
    main(rgs.dbhost, rgs.dbport, rgs.dbuser, rgs.user, rgs.date, rgs.outfile)
