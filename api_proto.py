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

df = pd.read_csv('data/bangalore-wards-2020-1-All-MonthlyAggregate.csv')

with open('data/bangalore_wards.json') as f:
    ward_data = json.load(f)

# def load_od_data():

#     od_map = {}
#     for _, r in df.iterrows():
#         od_map[str(r['Destination Movement ID'])] = {
#             'mean_travel_sec': r['Mean Travel Time (Seconds)'],
#             'min_travel_sec': r['Range - Lower Bound Travel Time (Seconds)'],
#             'max_travel_sec': r['Range - Upper Bound Travel Time (Seconds)']
#         }

#     return od_map

# od_map = load_od_data()

@app.get("/od_api/get_od_data")
def get_od_data(id: str = '1'):
    return parse_data(id)

def get_time_val(df):
    val = df.values

    if len(val) == 0:
        return 0
    return val[0]

@app.get("/od_api/get_od_data_json")
def get_od_data_json(id: str = '1'):
    df_src = df[(df['sourceid'] == int(id)) & (df['month'] == 1)]
    ward = copy.deepcopy(ward_data)
    features = []
    for f in ward['features']:
        m_id = f['properties']['MOVEMENT_ID']

        df_dest = df_src[df_src['dstid'] == int(m_id)]

        f['properties'] = {
            'mean_travel_sec': get_time_val(df_dest['mean_travel_time']),
            'id': m_id,
            'name': f['properties']['WARD_NAME']
        }
        features.append(f)
    ward['features'] = features

    return ward



def parse_data(id: str):
    df_src = df[(df['sourceid'] == int(id)) & (df['month'] == 1)]
    res_obj = {
        'origin_id': int(id)
    }

    dest = {}

    for _, r in df_src.iterrows():
        dest[int(r['dstid'])] = {
            'mean_travel_time': r['mean_travel_time']
        }
    
    res_obj['destinations'] = dest

    # with open('data/od.json', 'w') as f:
    #     json.dump(res_obj, f)

    return res_obj
