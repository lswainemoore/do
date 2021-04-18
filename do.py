import argparse
import datetime
import os
import sqlite3

CONN = sqlite3.connect('do.db', detect_types=sqlite3.PARSE_DECLTYPES)

HOSTS_FILE = '/etc/hosts'
TMP_HOSTS_FILE = '/tmp/do_hosts'

DO_HOSTS_BLOCK_START = '# DO-BLOCK-START'
DO_HOSTS_BLOCK_END = '# DO-BLOCK-END'

BLOCK_DEFAULT = 60
BREAK_DEFAULT = 5


class DoSession(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def time_left(self):
        return self.start_time + datetime.timedelta(minutes=self.duration) - datetime.datetime.utcnow()

    @property
    def is_elapsed(self):
        return self.time_left <= datetime.timedelta(0)


def results(cur):
    labels = [d[0] for d in cur.description]
    for row in cur:
         yield DoSession(**dict(zip(labels, row)))


def better_fetch_all(cur):
    return [r for r in results(cur)]


def read_sites():
    with open('sites.txt') as f:
        return [s.strip() for s in f]


def write_with_newline(f, line):
    f.write(line)
    f.write('\n')


def flush_dns_cache():
    # a little unclear if this is actually useful.
    # https://superuser.com/a/346519
    os.system('sudo dscacheutil -flushcache')


def block_sites(duration=BLOCK_DEFAULT):
    sites = read_sites()

    # always unblock so we can add to the end
    # little slower, but just easier.
    unblock_sites()

    # copy whole file to tmp
    with open(HOSTS_FILE, 'r') as f:
        with open(TMP_HOSTS_FILE, 'w') as g:
            for line in f:
                g.write(line)

    # re-open to add new lines
    with open(TMP_HOSTS_FILE, 'a') as g:
        write_with_newline(g, DO_HOSTS_BLOCK_START)
        for site in sites:
            write_with_newline(g, f'127.0.0.1\t{site}')
            # see: https://apple.stackexchange.com/a/359717
            write_with_newline(g, f':: {site}')
        write_with_newline(g,DO_HOSTS_BLOCK_END)

    os.replace(TMP_HOSTS_FILE, HOSTS_FILE)
    flush_dns_cache()

    # make a row for this block session
    cur = CONN.cursor()
    cur.execute("""
        INSERT INTO do_session (
            mode,
            start_time,
            duration
        ) VALUES (
            'blocking',
            ?,
            ?
        );""",
        (
            datetime.datetime.utcnow(),
            duration
        )
    )
    CONN.commit()


def unblock_sites():
    # basically just remove the block.
    # tmp file pattern from: https://stackoverflow.com/a/26912445
    with open(HOSTS_FILE, 'r') as f:
        with open(TMP_HOSTS_FILE, 'w') as g:
            copying = True
            for line in f:
                if line.strip() == DO_HOSTS_BLOCK_START:
                    copying = False
                if copying:
                    g.write(line)
                if line.strip() == DO_HOSTS_BLOCK_END:
                    copying = True
    os.replace(TMP_HOSTS_FILE, HOSTS_FILE)
    flush_dns_cache()

    # anything that was blocked is no longer so
    cur = CONN.cursor()
    cur.execute("""
        UPDATE do_session
        SET actual_end_time = ?
        WHERE mode = 'blocking'
        """,
        (datetime.datetime.utcnow(),)
    )
    CONN.commit()


def start_break(duration=BREAK_DEFAULT):
    cur = CONN.cursor()
    cur.execute("""
        INSERT INTO do_session (
            mode,
            start_time,
            duration
        ) VALUES (
            'breaking',
            ?,
            ?
        );""",
        (
            datetime.datetime.utcnow(),
            duration
        )
    )
    CONN.commit()


def end_break():
    cur = CONN.cursor()
    cur.execute("""
        UPDATE do_session
        SET actual_end_time = ?
        WHERE mode = 'breaking'
        """,
        (datetime.datetime.utcnow(),)
    )
    CONN.commit()


def get_open_session():
    cur = CONN.cursor()
    cur.execute("""
        SELECT *
        FROM do_session
        WHERE actual_end_time IS NULL
        ORDER BY start_time desc
        LIMIT 1
        """)
    sessions = better_fetch_all(cur)
    if sessions:
        return sessions[0]
    return None


def current_session_mode():
    session = get_open_session()
    return session.mode


def is_currently_in_mode(mode):
    return current_session_mode() == mode


def is_currently_blocking():
    return is_currently_in_mode('blocking')


def is_currently_breaking():
    return is_currently_in_mode('breaking')


if __name__ == '__main__':
    pass
