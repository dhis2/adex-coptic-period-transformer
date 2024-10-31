import datetime
import os
import re

from flask import Flask, request, jsonify
import requests
from ethiopian_date import EthiopianDateConverter
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
    app.logger.debug(f'Received request data: {request.data}')

    try:
        data = request.json
        app.logger.debug(f'Parsed JSON data: {data}')
    except Exception as e:
        app.logger.error(f'Error parsing JSON: {e}')
        return jsonify({'error': 'Invalid JSON format'}), 400

    data['dataValues'] = handle_thirteenth_month(data['dataValues'])
    data['dataValues'] = handle_storedby(data['dataValues'])
    data['dataValues'] = handle_period(data['dataValues'])

    app.logger.debug(f'Converted data values: {data}')
    request_params = request.args
    app.logger.debug(f'Request parameters: {request_params}')
    credentials = request.headers.get('Authorization')
    app.logger.debug(f'Credentials: {credentials}')
    # Set the X-Forwarded-For header to the remote address
    forwarded_for = request.headers.get('X-Forwarded-For')
    remote_addr = request.remote_addr
    if forwarded_for:
        forwarded_for = forwarded_for + ', ' + remote_addr
    else:
        forwarded_for = remote_addr

    target_url = base_url + "/api/dataValueSets"
    headers = {'Authorization': credentials, 'X-Forwaded-For': forwarded_for, 'Content-Type': 'application/json'}
    app.logger.debug(f'Sending request to {target_url} with headers: {headers}')

    response = requests.post(target_url, json=data, headers=headers, params=request_params)

    return jsonify(response.json()), response.status_code


def convert_ethiopian_period(period):
    month_period_pattern = re.compile(r'^(\d{6})$')
    quarter_period_pattern = re.compile(r'^(\d{4})Q(\d)$')
    year_period_pattern = re.compile(r'^(\d{4})$')
    daily_period_pattern = re.compile(r'^(\d{8})$')
    weekly_period_pattern = re.compile(r'^(\d{4})W(\d+)$')

    if month_period_pattern.match(period):
        greg_period = convert_ethiopian_month(period)
        app.logger.debug(f'Converting monthly period: {period} to {greg_period}')
    elif quarter_period_pattern.match(period):
        greg_period = convert_ethiopian_quarter(period)
        app.logger.debug(f'Converting quarterly period: {period} to {greg_period}')
    elif year_period_pattern.match(period):
        greg_period = convert_ethiopian_year(period)
        app.logger.debug(f'Converting yearly period: {period} to {greg_period}')
    elif daily_period_pattern.match(period):
        greg_period = convert_ethiopian_day(period)
        app.logger.debug(f'Converting daily period: {period} to {greg_period}')
    elif weekly_period_pattern.match(period):
        greg_period = convert_ethiopian_week(period)
        app.logger.debug(f'Converting weekly period: {period} to {greg_period}')
    elif True:
        app.logger.debug(f'Period {period} is not a valid Ethiopian period')
        greg_period = period
    return greg_period


def get_last_day_ethiopian_month(year, month):
    if month != 13:
        return 30
    else:
        if (year % 4) == 3:
            return 6
        else:
            return 5


def convert_ethiopian_quarter(period):
    conv = EthiopianDateConverter.to_gregorian
    ethiopian_year = int(period[:4])
    ethiopian_quarter = int(period[-1:])
    ethiopian_month = ethiopian_quarter * 3
    if ethiopian_month == 12:
        ethiopian_month = 13
    last_day = get_last_day_ethiopian_month(ethiopian_year, ethiopian_month)
    gregorian_date = conv(ethiopian_year, ethiopian_month, last_day)
    quarter = (gregorian_date.month - 1) // 3 + 1
    return f'{gregorian_date.year}Q{quarter}'


def convert_ethiopian_month(period):
    conv = EthiopianDateConverter.to_gregorian
    ethiopian_year = int(period[:4])
    ethiopian_month = period[-2:]
    if ethiopian_month[0] == '0':
        ethiopian_month = ethiopian_month[1]
    ethiopian_month = int(ethiopian_month)
    last_day = get_last_day_ethiopian_month(ethiopian_year, ethiopian_month)
    gregorian_date = conv(ethiopian_year, ethiopian_month, last_day)
    return gregorian_date.strftime('%Y%m')


def convert_ethiopian_year(period):
    conv = EthiopianDateConverter.to_gregorian
    ethiopian = int(period)
    # Get the last day of the coptic year
    ethiopian_last_day = get_last_day_ethiopian_month(ethiopian, 13)
    gregorian_date = conv(ethiopian, 13, ethiopian_last_day)
    return gregorian_date.strftime('%Y')


def convert_ethiopian_day(period):
    conv = EthiopianDateConverter.to_gregorian
    ethiopian_year = int(period[:4])
    ethiopian_month = int(period[4:6])
    ethiopian_day = int(period[6:])
    gregorian_date = conv(ethiopian_year, ethiopian_month, ethiopian_day)
    return gregorian_date.strftime('%Y%m%d')


def extract_week_chars(s):
    match = re.search(r'W(\d+)$', s)
    if match:
        return match.group(1)
    return None


def convert_ethiopian_week(period):
    conv = EthiopianDateConverter.to_gregorian
    ethiopian_year = int(period[:4])
    ethiopian_week = int(extract_week_chars(period))
    gregorian_date = conv(ethiopian_year, 1, 1)
    gregorian_date += datetime.timedelta(weeks=ethiopian_week - 1)
    week_number = gregorian_date.isocalendar()[1]
    return f'{gregorian_date.year}W{week_number}'


def handle_period(datavalues):
    for data_value in datavalues:
        data_value['period'] = convert_ethiopian_period(data_value['period'])
    return datavalues


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
