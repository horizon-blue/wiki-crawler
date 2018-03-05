import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from config import DATABASE_FILE, DIR_PATH

# get the absolute path of current directory
DATABASE_ADDRESS = "sqlite:///{}/{}".format(DIR_PATH, DATABASE_FILE)

database_address = "sqlite:///:memory:" if os.environ.get("UNITTEST") else DATABASE_ADDRESS

# reference: http://flask.pocoo.org/docs/0.12/patterns/sqlalchemy/

engine = create_engine(database_address, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


# for quick setup, this should be run to initialize the database for the first time
def init_db():
    # noinspection PyUnresolvedReferences
    from model.graph import Edge, Movie, Actor
    Base.metadata.create_all(bind=engine)
