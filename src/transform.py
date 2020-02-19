import pandas as pd
import numpy as np
import pymongo
import requests
import logging
import logging.handlers
import json
import glob
import io
import os


with open('src/metadata.json') as md_file:
    metadata = json.load(md_file)


def retrieve_csv(url):
    r = requests.get(url, 
                     headers = {'Content-Type': 'application/json', 
                                'User-Agent': 'danjrauch'})
    r.raise_for_status
    r = requests.get(r.json()['download_url'], 
                     headers = {'Content-Type': 'application/json', 
                                'User-Agent': 'danjrauch'})
    r.raise_for_status
    df = pd.read_csv(io.StringIO(r.text))
    return df


def transform_time_series_file(df, type):
    data = []
    for idx, row in df.iterrows():
        element = {}
        for col_name, v in row.items():
            if col_name in metadata['time_series']['column_names']:
                element[col_name.lower()] = v
            else:
                element['date'] = col_name
                element[type] = v
                data.append(element)
    return data


def retrieve_time_series_data():
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['corona']
    time_series_col = db['time_series']

    time_series_col.remove({});

    agg = {}

    for type in ['confirmed', 'recovered', 'deaths']:
        # Retrieve the data from a file and construct a dataframe
        ts_df = retrieve_csv(metadata['time_series']['url'] + '/' + metadata['time_series'][type]['file_name'])
        ts_df = ts_df.fillna(value={'Province/State':'','Country/Region':''})

        # Transform into objects
        data = transform_time_series_file(ts_df, type)

        # Aggregate the objects
        for d in data:
            key = d['province/state']+d['country/region']+d['date']
            if key in agg:
                agg[key][type] = d[type]
            else:
                agg[key] = d

    data = []
    for val in agg.values():
        data.append(val)

    # Insert into Mongo
    x = time_series_col.insert_many(data)

if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler('app.log', maxBytes=10240, backupCount=5)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s '
                                  '[in %(filename)s:%(lineno)d]')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info('UPDATE: Started')
    retrieve_time_series_data()
    logger.info('UPDATE: Done')
