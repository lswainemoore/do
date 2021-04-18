set up db: `sqlite3 do.db < schema.sql`

build application: `python setup.py py2app -A`

n.b. we're using development mode, so that we can edit blocklist easily.
this of course raises q: why make an app at all?
a: mostly to get rid of annoying dock icon.

run application: `sudo -b ./dist/do_app.app/Contents/MacOS/do_app`

note that for ^ we're not using `open` because sudo doesn't work. annoying!
