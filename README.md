# music-metadata
##Execution
Run this however you run flask apps. Outside of production environments you can use:

`$ flask --app music-metadata run --debug`

then access the app through your web browser at http://localhost:5000

Do not do NOT do this in any sort of production environment, it will allow any user with access to the server execute arbitrary code on your machine. Removing the --debug flag will make that slightly harder, but still don't do it. Use a real web server.

## TODO
- A UI that isn't ugly as sin
- Figure out how to order tracks based on soundexchange data
- Add deezer data to track list? Maybe this is how tracks get sorted? Maybe it's a separate list?
- More search options?
- Make enter key search