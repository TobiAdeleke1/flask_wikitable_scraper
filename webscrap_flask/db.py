import sqlite3
import typing as t

import click
from flask import current_app, g


def init_db() -> None:
    """Gets the database connection, and read sql schema to create the tables"""

    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))

@click.command('init-db')
def init_db_command()-> None:
    """Clear the existing data and calls init_db to create new tables"""

    init_db()
    click.echo('Initialized the database ..')

def get_db() -> t.Any:
    """ Create database connection if none exist,
        Else returns the connection that already exist in g
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    
    return g.db

def close_db(e=None) -> None:
    """ Close any database connection that exists in g """
    db = g.pop('db', None)

    if db is not None:
        db.close()
        
def init_app(app) -> None:
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

