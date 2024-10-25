import datetime
import os
import re

from flask import Flask, request, jsonify
import requests
from convertdate import coptic
import logging
import configparser

app = Flask(__name__)

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)


@app.route('/api/dataValueSets', methods=['POST'])
def process_request():
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    config.read(config_path)
    base_url = config.get('General', 'base_url')
    # Log the raw incoming request
    app.logger.debug(f'Received request data: {request.data}')

    # Try to parse the JSON payload
    try:
        data = request.json
        app.logger.debug(f'Parsed JSON data: {data}')
    except Exception as e:
        app.logger.error(f'Error parsing JSON: {e}')
        return jsonify({'error': 'Invalid JSON format'}), 400

    data['dataValues'] = handle_thirteenth_month(data['dataValues'])
    data['dataValues'] = handle_storedby(data['dataValues'])

    for data_value in data['dataValues']:
        data_value['period'] = convert_coptic_period(data_value['period'])
    app.logger.debug(f'Converted data values: {data}')
    request_params = request.args
    app.logger.debug(f'Request parameters: {request_params}')
    credentials = request.headers.get('Authorization')
    app.logger.debug(f'Credentials: {credentials}')

    target_url = base_url + "/api/dataValueSets"
    headers = {'Authorization': credentials, 'Content-Type': 'application/json'}

    response = requests.post(target_url, json=data, headers=headers, params=request_params)

    return jsonify(response.json()), response.status_code


def convert_coptic_period(period):
    month_period_pattern = re.compile(r'(\d{6})')
    quarter_period_pattern = re.compile(r'(\d{4})Q(\d)')
    year_period_pattern = re.compile(r'(\d{4})')

    if month_period_pattern.match(period):
        greg_period = convert_coptic_month(period)
        app.logger.debug(f'Converting monthly period: {period} to {greg_period}')
    elif quarter_period_pattern.match(period):
        greg_period = convert_coptic_quarter(period)
        app.logger.debug(f'Converting quarterly period: {period} to {greg_period}')
    elif year_period_pattern.match(period):
        greg_period = convert_coptic_year(period)
        app.logger.debug(f'Converting yearly period: {period} to {greg_period}')
    elif True:
        app.logger.debug(f'Period {period} is not a valid Coptic period')
        greg_period = period
    return greg_period


def get_last_day_coptic_month(year, month):
    cal = coptic.monthcalendar(year, month)
    if len(cal) == 4:
        if cal[3][0] == 0:
            last_day = cal[2][0]
        else:
            last_day = cal[3][0]
    else:
        last_day = cal[3][0]
    return last_day


def convert_coptic_quarter(period):
    coptic_year = int(period[:4])
    coptic_quarter = int(period[-1:])
    coptic_month = coptic_quarter * 3
    last_day = get_last_day_coptic_month(coptic_year, coptic_month)
    gregorian_date = coptic.to_gregorian(coptic_year, coptic_month, last_day)
    this_day = datetime.datetime(gregorian_date[0], gregorian_date[1], gregorian_date[2])
    quarter = (this_day.month - 1) // 3 + 1
    return f'{this_day.year}Q{quarter}'


def convert_coptic_month(period):
    coptic_year = int(period[:4])
    coptic_month = period[-2:]
    if coptic_month[0] == '0':
        coptic_month = coptic_month[1]
    coptic_month = int(coptic_month)
    last_day = get_last_day_coptic_month(coptic_year, coptic_month)
    gregorian_date = coptic.to_gregorian(coptic_year, coptic_month, last_day)
    this_day = datetime.datetime(gregorian_date[0], gregorian_date[1], gregorian_date[2])
    return this_day.strftime('%Y%m')


def convert_coptic_year(period):
    coptic_year = int(period)
    # Get the last day of the coptic year
    gregorian_date = coptic.to_gregorian(coptic_year, 13, 30)
    this_day = datetime.datetime(gregorian_date[0], gregorian_date[1], gregorian_date[2])
    return this_day.strftime('%Y')


def handle_thirteenth_month(datavalues):
    regex = re.compile(r'(\d{4})13')
    for data_value in datavalues:
        if regex.match(data_value['period']):
            datavalues.remove(data_value)
    return datavalues


def handle_storedby(datavalues):
    for data_value in datavalues:
        data_value.pop('storedby', None)
    return datavalues


if __name__ == '__main__':
    app.run(debug=True)
