#!/usr/bin/python3

DEEZER_API = 'https://api.deezer.com'
SX_API='https://isrc-api.soundexchange.com/api/ext'

from flask import Flask, jsonify, render_template, request

import requests

from pprint import pp as pprint



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
def getAlbumDataFromTrack():
    trackID=request.args.get('deezerID')
    track = requests.get(url=f'{DEEZER_API}/track/{trackID}').json()
    return formAlbumOutput(track['album']['id'])



def formAlbumOutput(deezerID):
    dzData = requests.get(url=f'{DEEZER_API}/album/{deezerID}').json()

    sxSession = soundexchangeSession()
    sxData = sxSession.post(f'{SX_API}/recordings', json={  "searchFields": {"icpn": dzData['upc']},
                                                            "start": 0,
                                                            "number": 100,
                                                            "showReleases": True
                                                            }).json()

    tracks = buildTracks(dzData,sxData, sxSession)

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

def buildTracks(dzData,sxData,sxSession):
    tracks = []

    for record in dzData['tracks']['data']:
        track = {'dz' : {}, 'sx' : {}}
        dzTrack = requests.get(url=f'{DEEZER_API}/track/{record['id']}').json()
        sxTracks = [track for track in sxData['recordings'] if track['isrc'] == dzTrack['isrc']]
        if not sxTracks:
            sxRes = sxSession.post (f'{SX_API}/recordings/', json={ "searchFields": {"isrc":dzTrack['isrc']},
                                                                    "start": 0,
                                                                    "number": 100,
                                                                    "showReleases": True
                                                                    }).json()
            if sxRes['numberOfRecordings']:
                sxTracks = sxRes['recordings']

        track['dz'] |= {    'title': dzTrack['title'],
                            'track': dzTrack['track_position'],
                            'disk': dzTrack['disk_number'],
                            'artist': dzTrack['artist']['name'],
                            'isrc': dzTrack['isrc'],
                            'artists': list(map(lambda artist: artist['name'], dzData['contributors'])),
                            'length': f'{int(dzTrack['duration'] / 60)}:{dzTrack['duration'] % 60}',
                            'date': dzTrack['release_date']
                            }
        if sxTracks:      
            track['sx'] |= {'title': [ e.get('recordingTitle') for e in sxTracks ],
                            'length': [ e.get('duration') for e in sxTracks ],
                            'version': [ e.get('recordingVersion') for e in sxTracks ],
                            'isrcValid': [ e.get('isValidIsrc') for e in sxTracks ],
                            'year': [ e.get('recordingYear') for e in sxTracks ],
                            'label': [ e.get('releaseLabel') for e in sxTracks ],
                            'date': [ e.get('releaseDate') for e in sxTracks ]
                            }
        tracks.append(track)
            
    return tracks



if __name__ == '__main__':
    deezerData.run(debug=True)
