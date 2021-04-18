## Huh??

Basically, [Self Control](https://selfcontrolapp.com/) + timer interface.

Also uses [rumps](https://github.com/jaredks/rumps), which I found out about from this handy article: https://camillovisini.com/article/create-macos-menu-bar-app-pomodoro/.

Use at your own risk!! Touches /etc/hosts and uses sudo, etc.


## Installation

set up db: `sqlite3 do.db < schema.sql`

build application: `python setup.py py2app -A`

n.b. we're using development mode, so that we can edit blocklist easily.
this of course raises q: why make an app at all?
a: mostly to get rid of annoying dock icon.

run application: `sudo -b ./dist/do_app.app/Contents/MacOS/do_app`

note that for ^ we're not using `open` because sudo doesn't work. annoying!

install in `crontab -e`: `*/10 * * * * pgrep -n "do_app" > /dev/null || ~/<path>/dist/do_app.app/Contents/MacOS/do_app`

(pgrep solution from: https://stackoverflow.com/a/30031040. note that i've added redirect to prevent us from getting mailed the pid.)
