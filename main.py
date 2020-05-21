from flask import Flask, render_template, Markup, request, jsonify,redirect
from flask_cors import CORS

import requests as r
from tmdbv3api import TMDb
import pandas as pd
import json
from tmdbv3api import TV
import uuid
import urllib.parse

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
        #shows_name = []
        shows_data = {'name':[], 'poster':[], 'uid':[], 'desc':[], 'status':[]}
        for index, row in shows.iterrows():
            if row.tmdb_ids!=0:
                similar = tv.similar(row.tmdb_ids)
            
                for show in similar:
                    #shows_name.append(show.name)
                    #print(show.name)
                    shows_data['name'].append(show.name)
                    shows_data['poster'].append(show.poster_path)
                    shows_data['desc'].append(show.overview)
                    uid =str(str(uuid.uuid1()).split('-')[0])
                    shows_data['uid'].append("t"+str(show.id)+"tv")
                    shows_data['status'].append(row.status)
                    #print(uuid.uuid1())

                    #print(show.overview)
        #df = (pd.DataFrame(shows_data))
        #return df['name'].tolist()
        #df.to_csv('./shows.csv')
        eshow = pd.DataFrame(shows_data)
        print(eshow['status'])
        #print(len(eshow))
        eshow.drop_duplicates(subset ="name", keep = False, inplace = True)
        print(len(eshow))
        return eshow
@app.route('/adds', methods=['POST'])
def add_series():
    #/api/series/lookup?term=The%20Blacklist&apikey=a45a1e77bedf4db29280d25ba6e47808
    
    #print(urllib.parse.quote(str("BLACK List")))
    
    #http://10.0.0.166:8989
    #shows = r.get('http://10.0.0.166:8989/api/series/lookup?term=s&apikey=a45a1e77bedf4db29280d25ba6e47808')
    #print(request.form['showname'])
    try:
        showname = str(urllib.parse.quote(request.form['showname']))
        show_content = json.loads(r.get('http://10.0.0.166:8989/api/series/lookup?term='+showname+'&apikey=a45a1e77bedf4db29280d25ba6e47808').content)
        show_data = pd.DataFrame(show_content)
        show_seasons = show_content[0]['seasons'][0]
        show_post = {
        "addOptions": {
        "ignoreEpisodesWithFiles": True,
        "ignoreEpisodesWithoutFiles": False,
        "searchForMissingEpisodes": True
        },
        'seasons':[],
        "title": show_content[0]['title'],
        "rootFolderPath": "/filerun/user-files/n2shows03/",
        "qualityProfileId": 1,
        "seasonFolder": True,
        "monitored": True,
        "tvdbId": show_content[0]['tvdbId'],
        "tvRageId": show_content[0]['tvRageId'],
        "cleanTitle": show_content[0]['cleanTitle'],
        "imdbId": show_content[0]['imdbId'],
        "titleSlug": show_content[0]['titleSlug'],
        "id": 0,
        "images": []
        }
        show_post['seasons'].append(show_seasons)
        print(json.dumps(show_post))
        #/api/series

        res = r.post("http://10.0.0.166:8989/api/series?apikey=a45a1e77bedf4db29280d25ba6e47808", data=json.dumps(show_post))
        print(res.text)
    except:
        print("show errorr")
        pass
    return redirect("/", code=302)

@app.route('/', methods=['GET'])
def index():
    g = request.args.get('ongoing', False)
    if g=='true':
        sdata = show_data.loc[show_data['status'] == 'continuing']
    elif g==False:
        sdata = show_data
    print(len(sdata))
    """try:
        #g = request.args.get('ongoing', False)
        
        #sdata = show_data['status']=='continuing'
        if request.args.get('ongoing', False):
            sdata = show_data.loc[show_data['status'] == 'continuing']
        #sdata = show_data
        #sdata = show_data['status']=='continuing'
        #sdata = show_data#['status']=='continuing'
    except KeyError as e:
        print ('I got a KeyError - reason "%s"' % str(e))
        sdata = show_data
    except IndexError as e:
        print ('I got an IndexError - reason "%s"' % str(e))
        sdata = show_data
    print(len(sdata))"""
    return render_template("index.html", shows=show_data )
if __name__ == "__main__":
    show_data = main()
    app.run(host='0.0.0.0', port=3000, debug=True)


