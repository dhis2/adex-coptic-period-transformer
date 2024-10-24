import datetime
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
    config.read('config.ini')
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
        period = period
    return period


def convert_coptic_quarter(period):
    coptic_year = int(period[:4])
    coptic_quarter = int(period[-1:])
    # Get the last day of the coptic quarter
    gregorian_date = coptic.to_gregorian(coptic_year, coptic_quarter * 3, 30)
    this_day = datetime.datetime(gregorian_date[0], gregorian_date[1], gregorian_date[2])
    quarter = (this_day.month - 1) // 3 + 1
    return f'{this_day.year}Q{quarter}'


def convert_coptic_month(period):
    coptic_year = int(period[:4])
    coptic_month = period[-2:]
    # Put the 13th month as the first month of the next year
    if coptic_month == '13':
        coptic_month = '01'
        coptic_year += 1
    # Strip the leading zero if present
    if coptic_month[0] == '0':
        coptic_month = coptic_month[1]
    coptic_month = int(coptic_month)
    gregorian_date = coptic.to_gregorian(coptic_year, coptic_month, 30)
    this_day = datetime.datetime(gregorian_date[0], gregorian_date[1], gregorian_date[2])
    return this_day.strftime('%Y%m')


def convert_coptic_year(period):
    coptic_year = int(period)
    # Get the last day of the coptic year
    gregorian_date = coptic.to_gregorian(coptic_year, 13, 30)
    this_day = datetime.datetime(gregorian_date[0], gregorian_date[1], gregorian_date[2])
    return this_day.strftime('%Y')


def convert_date_to_quarter_period(date):
    # Convert the date to a string in the format YYYYQ#
    this_day = datetime.datetime(date[0], date[1], date[2])
    quarter = (this_day.month - 1) // 3 + 1
    return f'{this_day.year}Q{quarter}'


if __name__ == '__main__':
    app.run(debug=True)
