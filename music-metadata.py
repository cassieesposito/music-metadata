#!/usr/bin/python3

DEEZER_API = 'https://api.deezer.com'
SX_API='https://isrc-api.soundexchange.com/api/ext'

from flask import Flask, jsonify, render_template, request

import requests
# import pprint



deezerData = Flask(__name__,static_url_path='')

@deezerData.route('/')
def index():
    return render_template('index.html')

@deezerData.route('/artist')
def getArtistData():
    artistID=request.args.get('deezerID')
    artist = requests.get(url=f'{DEEZER_API}/artist/{artistID}').json()
    output = {'id':artistID,
               'name': artist['name']}
    return jsonify(output)

@deezerData.route('/album')
def getAlbumData():
    return formAlbumOutput(request.args.get('deezerID'))

@deezerData.route('/track')
def getTrackData():
    trackID=request.args.get('deezerID')
    track = requests.get(url=f'{DEEZER_API}/track/{trackID}').json()
    return formAlbumOutput(track['album']['id'])



def formAlbumOutput(deezerID):
    dzData = requests.get(url=f'{DEEZER_API}/album/{deezerID}').json()

    session = soundexchangeSession()
    sxData = session.post(f'{SX_API}/recordings', json={
                                                "searchFields":{"icpn": dzData['upc']},
                                                "start":0,
                                                "number":100,
                                                "showReleases":True
                                                }).json()
    
    # pprint.pp(sxData)

    tracks = []
    for track in sxData['recordings']:
        tracks.append({ 'title': track['recordingTitle'],
                        'artists': track['recordingArtistName'].split(' ♦ '),
                        'length': track['duration'],
                        'version': track['recordingVersion'],
                        'year': track['recordingYear'],
                        'album': track['releaseName'],
                        'releaseLabel': track['releaseLabel'].split(' ♦ '),
                        'releaseDate': track['releaseDate']
                       })

    output = {'id':deezerID,
               'title': dzData['title'],
               'artist': dzData['artist']['name'],
               'deezerReleaseDate': dzData['release_date'],
               'upc': dzData['upc'],
               'label': dzData['label'],
               'tracks': tracks,
               'albumLink': dzData['link'],
               'artistLink': f'https://www.deezer.com/en/artist/{dzData["artist"]["id"]}'
               }
    return jsonify(output)


def soundexchangeSession():
    session = requests.session()
    session.get(f'{SX_API}/login')
    return session



if __name__ == '__main__':
    deezerData.run(debug=True)
