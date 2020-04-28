from flask import Flask, render_template, Markup, request, jsonify
from flask_cors import CORS

import requests as r
from tmdbv3api import TMDb
import pandas as pd
import json
from tmdbv3api import TV

tmdb = TMDb()
tmdb.api_key = 'c04a482fc905672130d1c1cbdbdfb61d'
tmdb.language = 'en'
tmdb.debug = True

app = Flask(__name__)
CORS(app)


tv = TV()
#show = tv.search('Breaking Bad')

def main():
    #http://10.0.0.166:8989/api/series?apikey=a45a1e77bedf4db29280d25ba6e47808
    sonarr_res = r.get('http://10.0.0.166:8989/api/system/status?apikey=a45a1e77bedf4db29280d25ba6e47808')
    if sonarr_res.status_code==200:
        shows = pd.DataFrame(json.loads(r.get('http://10.0.0.166:8989/api/series?apikey=a45a1e77bedf4db29280d25ba6e47808').content))
        #print(pd.DataFrame(shows))
        shows.imdbId.dropna(axis=0, how='any', inplace=True)
        #print(shows.imdbId)
        #https://api.themoviedb.org/3/find/tt3322312?api_key=c04a482fc905672130d1c1cbdbdfb61d&language=en-US&external_source=imdb_id
        tmdb_ids = []
        for index, row in shows.iterrows():
            get_tmdb = (json.loads(r.get('https://api.themoviedb.org/3/find/'+str(row.imdbId)+'?api_key=c04a482fc905672130d1c1cbdbdfb61d&language=en-US&external_source=imdb_id').content))
            #print(get_tmdb.content)
            try:
                tmdb_ids.append(get_tmdb['tv_results'][0]['id'])
                #print(get_tmdb['tv_results'][0])
            except IndexError:
                tmdb_ids.append(0)
        shows['tmdb_ids'] = tmdb_ids
        #print(shows.tmdb_ids)
        shows_name = []
        for index, row in shows.iterrows():
            if row.tmdb_ids!=0:
                similar = tv.similar(row.tmdb_ids)
            
                for show in similar:
                    shows_name.append(show.name)
                    #print(show.name)
                    #print(show.overview)
        df = (pd.DataFrame(shows_name))
        df.to_csv('./shows.csv')

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)


