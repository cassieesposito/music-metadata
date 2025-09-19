#!/usr/bin/python3

# Reference Deezer IDs
# Album 302309: The Highwaymen - The Road goes on Forever
# Track 30644201: Afroman - I feel Good from Waiting to Inhale
# Album 592830302: John Kirby - The Classics Sampler (missing ISRCs)

import asyncio
from aiohttp import web
import aiohttp

from pprint import pp as pprint

DEEZER_API = 'https://api.deezer.com'
SX_API='https://isrc-api.soundexchange.com/api/ext'
SX_RESULTS=100

###########
#  Setup  #
###########
def app():
    app = web.Application()
    app.add_routes([
        web.get('/', index),
        web.static('/', 'static'),
        # web.get('/artist', getArtistData),
        web.get('/album', getAlbumData),
        web.get('/track', getAlbumDataFromTrack)
    ])
    app.on_startup.append(onStartup)
    app.on_cleanup.append(onCleanup)
    return app

async def onStartup(app):
    app['session'] = aiohttp.ClientSession()

async def onCleanup(app):
    await app['session'].close()


############
#  Routes  #
############
async def index(req):
    return web.FileResponse('static/index.html')


# async def getArtistData(req):
#     session = req.app['session']
#     artistID = req.query['deezerID']
    
#     async with session.get(url=f'{DEEZER_API}/artist/{artistID}') as res:
#         artist = await res.json()
    
#     output = {'id':artistID,
#             'name': artist['name'],
#     }

#     return web.json_response(output)


async def getAlbumData(req):
    session = req.app['session'] 
    albumID = req.query['deezerID']

    album = Album()
    await album.albumInit(session,albumID)
    pprint (vars(album))

    return web.json_response(vars(album))


async def getAlbumDataFromTrack(req):
    session = req.app['session'] 
    trackID = req.query['deezerID']

    track = await get(session, f'{DEEZER_API}/track/{trackID}')
    albumID = track['album']['id']

    album = Album()
    await album.albumInit(session,albumID)
    print (vars(album))

    return web.json_response(vars(album))


#####################
#  Data Processing  #
#####################
class Album:
    def __init__(self):
        self.deezerId = None
        self.title = None
        self.artist = None
        self.deezerReleaseDate = None
        self.upc = None
        self.label = None
        self.albumLink = None
        self.artistLink = None
        self.tracks = []


    async def albumInit(self, session, albumID):
        data = {'dzAlbum': {}, 'sxAlbum': {}, 'dzTracks': [], 'sxTracks': {}}
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._sxLogin(session))
            res = tg.create_task(self._getDzAlbum(session, albumID))
        data['dzAlbum'] = res.result()

        async with asyncio.TaskGroup() as tg:
            data['dzTracks'] = tg.create_task(self._getDzTracks(session, data))
            data['sxAlbum'] = tg.create_task(self._getSxAlbum(session,data))
        data['dzTracks'] = await data['dzTracks']
        data['sxAlbum'] = await data['sxAlbum']

        data['sxTracks'] = await self._getSxTracks(session,data)

        self._populateVars(data)


    async def _sxLogin(self, session):
        return await get(session, f'{SX_API}/login')


    async def _getDzAlbum (self, session, albumID):
        dzAlbum = await get(session,f'{DEEZER_API}/album/{albumID}')
        return dzAlbum


    async def _getDzTracks (self, session, data):
        trackIDs = list(map(lambda data: data['id'], data['dzAlbum']['tracks']['data']))
        async with asyncio.TaskGroup() as tg:
            res = [tg.create_task(get(session,f'{DEEZER_API}/track/{id}')) for id in trackIDs]
        dzTracks = await asyncio.gather(*res)
        return dzTracks


    async def _getSxAlbum (self, session, data):
        payload = {
            "searchFields": {"icpn": data['dzAlbum']['upc']},
            "start": 0,
            "number": SX_RESULTS,
            "showReleases": True
        }
        return await post(session, f'{SX_API}/recordings', payload)


    async def _getSxTracks (self, session, data):
        # Create dict: sxTracks with the format {isrc: [sxTrackData]}. Populate it with data from data['sxAlbum']
        sxTracks = {}
        for dzTrack in data['dzTracks']:
            sxTracks[dzTrack['isrc']] = [sxTrack for sxTrack in data['sxAlbum']['recordings']
                                         if sxTrack['isrc'] == dzTrack['isrc']]

        # Query soundexchange for information about any tracks that were not included in the album
        # query and populate sxTracks['isrc'] with the results
        missingISRCs = [track['isrc'] for track in data['dzTracks'] if not sxTracks[track['isrc']]]
        missingSxTracks = []
        payload = {"searchFields": {"isrc": None}, "start": 0, "number": SX_RESULTS, "showReleases": True}
        async with asyncio.TaskGroup() as tg:
            for isrc in missingISRCs:
                payload['searchFields']['isrc'] = isrc
                missingSxTracks.append(asyncio.create_task(post(session,f'{SX_API}/recordings/',payload)))
        missingSxTracks = await asyncio.gather(*missingSxTracks)
        for track in missingSxTracks:
            print (track)
            print ("-----------------END MISSING TRACK-----------------")

        return sxTracks


    def _populateVars(self, data):
        self.deezerId = data['dzAlbum']['id']
        self.title = data['dzAlbum']['title']
        self.artist = data['dzAlbum']['artist']['name']
        self.deezerReleaseDate = data['dzAlbum']['release_date']
        self.upc = data['dzAlbum']['upc']
        self.label = data['dzAlbum']['label']
        self.albumLink = data['dzAlbum']['link']
        self.artistLink = f'https://www.deezer.com/artist/{data['dzAlbum']['artist']['id']}'
        for track in data['dzTracks']:
            self.tracks.append(self._buildTrack(track, data))
        return


    def _buildTrack (self, dzTrack, data):
        isrc = dzTrack['isrc']
        output = {'dz' : {}, 'sx' : {}}
        output['dz'] = {
            'title': dzTrack['title'],
            'track': dzTrack['track_position'],
            'disk': dzTrack['disk_number'],
            'artist': dzTrack['artist']['name'],
            'isrc': isrc,
            'artists': list(map(lambda artist: artist['name'], dzTrack['contributors'])),
            'length': f'{int(dzTrack['duration'] / 60)}:{str(dzTrack['duration'] % 60).zfill(2)}',
            'date': dzTrack['release_date']
            }
        output['sx'] = {
            'title': [ e.get('recordingTitle') for e in data['sxTracks'][isrc] ],
            'length': [ e.get('duration') for e in data['sxTracks'][isrc] ],
            'version': [ e.get('recordingVersion') for e in data['sxTracks'][isrc] ],
            'isrcValid': [ e.get('isValidIsrc') for e in data['sxTracks'][isrc] ],
            'year': [ e.get('recordingYear') for e in data['sxTracks'][isrc] ],
            'label': [ e.get('releaseLabel') for e in data['sxTracks'][isrc] ],
            'date': [ e.get('releaseDate') for e in data['sxTracks'][isrc] ]
            }
        return output


##################
#  HTTP Methods  #
##################
async def get(session, url, params=dict()):
    async with session.get(url, params=params) as res:
        return await res.json()


async def post(session, url, payload):
    async with session.post(url, json=payload) as res:
        return await res.json()


if __name__ == "__main__":
    web.run_app(app(), port=5000)