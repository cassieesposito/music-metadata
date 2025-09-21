# music-metadata
This webapp takes Deezer album or track IDs as input and returns the data necessary to add a release to the MusicBrainz database

##Execution
`$ ./music_metadata`

If you want a development environment, `pip install aiohttp-devtools` and then launch with `adev runserver --livereload -p 5000 ./music-metadata.py`

Once the server is running you can access the app through your web browser at http://localhost:5000


## TODO
- A UI that isn't ugly as sin (I don't really have these skills. Someone help?)
- More search options?
- CLI?
- Push data directly to MusicBrainz?
- Identify albums using other input methods? (spotify metadata? isrc?)
- Add release type