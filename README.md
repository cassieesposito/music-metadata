# music-metadata
This webapp takes Deezer album or track IDs as input and returns the data necessary to add a release to the MusicBrainz database

##Execution
Run this however you run flask apps. Outside of production environments you can use:

`$ flask --app music-metadata run --debug`

then access the app through your web browser at http://localhost:5000

Do not do NOT do this in any sort of production environment, it will allow any user with access to the server execute arbitrary code on your machine. Removing the --debug flag will make that slightly harder, but still don't do it. Use a real web server.

## TODO
- A UI that isn't ugly as sin (I don't really have these skills. Someone help?)
- More search options?
- Make enter key search
- Handle cases where soundexchange returns multiple results for a single isrc. This will have to wait until I find such a case. I've found them before, but I've forgotten which ones
  - Select from options when multiple results are returned by soundexchange?
- CLI?
- Push data directly to MusicBrainz?
- Identify albums using other input methods (spotify metadata? isrc?)

