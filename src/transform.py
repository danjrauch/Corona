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
                data.append(element.copy())
    return data


def retrieve_time_series_data():
    agg = {}

    types = ['confirmed', 'recovered', 'deaths']

    for type in types:
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

        for k, v in agg.items():
            for type in types:
                if type not in v:
                    v[type] = 0

        for k, v in agg.items():
            for type in types:
                if type not in v:
                    print('Value is missing: ')
                    print(v)

    df_agg = pd.DataFrame(agg.values(), columns=['province/state', 'country/region', 'lat', 'long', 'date', 'confirmed', 'recovered', 'deaths'])

    return df_agg


def save_to_cloud(df, database_name, collection_name):
    client = pymongo.MongoClient('mongodb+srv://pathogen:OdX2kR9DmzPLmuXk@corona-lvqsz.azure.mongodb.net/test?retryWrites=true&w=majority')
    db = client[database_name]
    col = db[collection_name]

    col.delete_many({})

    # df_agg.to_csv('here.csv', encoding='utf-8', index=False)

    data = []
    for idx, row in df.iterrows():
        data.append(row.to_dict())

    # Insert into Mongo
    x = col.insert_many(data)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler('app.log', maxBytes=10240, backupCount=5)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s '
                                  '[in %(filename)s:%(lineno)d]')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info('UPDATE: Started')
    df = retrieve_time_series_data()
    save_to_cloud(df, 'corona', 'time_series')
    logger.info('UPDATE: Done')
