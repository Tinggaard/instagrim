import sqlite3
import click
from os import mkdir
from shutil import rmtree
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """ Obtain the database connection, create one if it does not exist. """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """ Close the database connection if it is open. """
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """ Initialize a new empty database according to schema. """
    db = get_db()
    rmtree('instance\\images')
    mkdir('instance\\images')

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """ CLI wrapper to initialize new empty database. """
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """ Register database methods with the app. """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
