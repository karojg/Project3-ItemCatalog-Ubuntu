from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from catalogdb_setup import User, Category, CategoryItem

Base = declarative_base()

engine = create_engine('sqlalchemy://catalog:password@localhost/catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


category1 = Category(title="Biographies")
session.add(category1)
session.commit()

category2 = Category(title="Computers & Tech")
session.add(category2)
session.commit()

category3 = Category(title="Cooking")
session.add(category3)
session.commit()

category4 = Category(title="Romance")
session.add(category4)
session.commit()

category5 = Category(title="Travel")
session.add(category5)
session.commit()


print "added menu items!"
