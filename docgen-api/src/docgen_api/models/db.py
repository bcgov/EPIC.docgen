"""Initilizations for db, migration and marshmallow."""

from contextlib import contextmanager

from flask import current_app, g
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.plugins import PropertyModTrackerPlugin


# DB initialize in __init__ file
# db variable use for create models from here
db = SQLAlchemy()
make_versioned(user_cls=None, plugins=[PropertyModTrackerPlugin()])
# Migrate initialize in __init__ file
# Migrate database config
migrate = Migrate()

# Marshmallow for database model schema
ma = Marshmallow()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    # Using the default session for the scope
    session = db.session
    try:
        yield session
        session.commit()
    except Exception as e:  # noqa: B901, E722
        print(str(e))
        session.rollback()
        raise


@event.listens_for(db.session, "before_flush")
def before_commit(session, *args):  # pylint: disable=unused-argument
    """Listen to the  and updates the created_by/updated_by fields."""
    new_objects = session.new
    updated_objects = session.dirty
    username = g.jwt_oidc_token_info.get("preferred_username", None)
    current_app.logger.info("Before commit event. Updating created/updated by")
    current_app.logger.info(f"Preferred username is {username}")

    if username is None:
        username = g.jwt_oidc_token_info.get("email")
    for new_object in new_objects:
        setattr(new_object, "created_by", username)
    for updated_object in updated_objects:
        setattr(updated_object, "updated_by", username)
