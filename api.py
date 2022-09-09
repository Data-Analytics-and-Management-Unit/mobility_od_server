import json
import copy
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open('data/bangalore_wards.json') as f:
    bangalore_ward_data = json.load(f)

df_taxi = pd.read_csv('data/bangalore-wards-2020-1-All-MonthlyAggregate.csv')
df_od_driving = pd.read_csv('analysis/bangalore_od_travelling.csv')
df_od_transit = pd.read_csv('analysis/bangalore_od_transit.csv')

def get_time_val(df):
    return int(df.values.sum())

def get_data(mode, stats):
    if mode == 'driving' and stats == 'average_travel_time':
        return df_od_driving[['sourceid', 'destid', 'distance', 'duration']]
    elif mode == 'driving' and stats == 'max_travel_time':
        df = df_od_driving[['sourceid', 'destid', 'distance', 'duration_in_traffic']]
        df.columns = ['sourceid', 'destid', 'distance', 'duration']
        return df
    elif mode == 'transit':
        return df_od_transit[['sourceid', 'destid', 'distance', 'duration', 'fare']]

def get_properties(df, mode):
    p = {
        'time': get_time_val(df['duration']),
        'distance': get_time_val(df['distance'])
    }
    if mode == 'transit':
        p['fare'] = int(df['fare'].values.sum())

    return p
    

 
@app.get("/od_api/get_od_data")
def get_od_data(id: str = '1', mode: str = 'driving', stats: str = 'average_travel_time'):
    df = get_data(mode, stats)

    df_src = df[df['sourceid'] == int(id)]
    res_obj = {
        'origin_id': int(id)
    }

    dest = {}

    for _, r in df_src.iterrows():
        dest[int(r['destid'])] = {
            'time': int(r['duration']),
            'distance': int(r['distance'])
        }
        if mode == 'transit':
            dest[int(r['destid'])]['fare'] = int(r['fare'])
    
    res_obj['destinations'] = dest
    return res_obj

@app.get("/od_api/get_od_data_json")
def get_od_data_json(id: str = '1', mode: str = 'driving', stats: str = 'average_travel_time'):
    df = get_data(mode, stats)
    df_src = df[df['sourceid'] == int(id)]
    ward = copy.deepcopy(bangalore_ward_data)
    features = []
    
    for f in ward['features']:
        m_id = f['properties']['WARD_NO']

        df_dest = df_src[df_src['destid'] == int(m_id)]

        # print(df_dest)

        props = get_properties(df_dest, mode)

        props['id'] = m_id
        props['name'] = f['properties']['WARD_NAME']

        f['properties'] = props
        
        features.append(f)
    ward['features'] = features

    return ward




