from flask import Blueprint, jsonify, g, request, Response
import json
from datetime import datetime
import sqlite3

DATABASE = './iot.sqlite'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

mocked = Blueprint('mocked', __name__)

data = {}
with open('db.json', 'r') as file:
    data = json.load(file)

@mocked.route('/channels', methods=['GET'])
def m_channels():
    channels = _get_chanels()
    return jsonify(channels)

@mocked.route('/sensors', methods=['GET'])
def m_sensors():
    sensors = _get_sensors()
    return jsonify(sensors)

@mocked.route('/samples', methods=['GET'])
def m_samples():
    try:
        # recieved '2023-01-01T00:00:00.000Z' need remove the fiinal Z
        start = request.args['start'][:-1]
        end = request.args['end'][:-1]
    except:
        return Response('{"error": "Missing some of the required query parameters.}', status=201)

    samples = _get_samples(start, end)
    return jsonify(samples)


def _get_samples(start, end):
    data = dict()
    timestamps = []

    # to js timestamp * 1000
    start = datetime.fromisoformat(start).timestamp() * 1000
    end = datetime.fromisoformat(end).timestamp() * 1000

    print('Start - End', start, end)

    res = query_db('SELECT sensor_id, channel_id, timestamp, value FROM samples WHERE timestamp >= ? AND timestamp <= ? ORDER BY timestamp', (int(start), int(end)))

    for sample in res:
        print('Sample:', sample)
        sensor_id = sample[0]
        channel_id = sample[1]
        timestamp = sample[2]
        value = sample[3]

        if (len(timestamps) == 0 or timestamps[-1] != timestamp):
            timestamps.append(timestamp)

        data[sensor_id] = data.get(sensor_id, {})
        data[sensor_id][channel_id] = data[sensor_id].get(channel_id, [])
        data[sensor_id][channel_id].append(value);

    print('Data:', data)
    res = dict(
        count = len(timestamps),
        timestamps = [t for t in timestamps],
        data = data
    )

    return res

def _get_sensors():
    sensors = []
    res = query_db('SELECT id, name, description, group_name, object_id, location_x, location_y, location_z FROM sensors')

    for sensor in res:
        sensors.append(
            dict(
                id = sensor[0],
                name = sensor[1],
                description = sensor[2],
                groupName = sensor[3],
                objectId = sensor[4],
                location = dict(
                    x = sensor[5],
                    y = sensor[6],
                    z = sensor[7]
                )
            )
        )
    return sensors

def _get_chanels():
    channels = []
    res = query_db('SELECT id, name, description, unit, min, max FROM channels')

    for channel in res:
        channels.append(
            dict(
                id = channel[0],
                name = channel[1],
                description = channel[2],
                unit = channel[3],
                min = channel[4],
                max = channel[5]
            )
        )

    return channels
