#!/usr/bin/env python
# -*- coding: Utf-8 -*-

import logging
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, scoped_session

logger = logging.getLogger(__name__)

Base = declarative_base()
Session = scoped_session(sessionmaker())

recipe_tags = Table('recipe_tags', Base.metadata,
                    Column('recipe_id', Integer, ForeignKey('recipes.id')),
                    Column('tag_id', Integer, ForeignKey('tags.id')),
                    )

recipe_meals = Table('recipe_meals', Base.metadata,
                    Column('recipe_id', Integer, ForeignKey('recipes.id')),
                    Column('meal_id', Integer, ForeignKey('meals.id')),
                    )

class Recipe(Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    tags = relationship('Tag', secondary=recipe_tags, backref='recipes')

    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    def __repr__(self):  #pragma: no cover
        return '<Recipe: "%s">'%self.name


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):  #pragma: no cover
        return '<Tag: "%s">'%self.name

class Meal(Base):
    __tablename__ = 'meals'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    index = Column(Integer)
    recipes = relationship('Recipe', secondary=recipe_meals, backref='meals')

    def __init__(self, date, index, recipes=None):
        self.date = date
        self.index = index
        if recipes:
            self.recipes = recipes

    def __repr__(self):  #pragma: no cover
        return '<Meal: %s, %s, %s>'%(self.date, self.index, self.recipes)


def populate():
    session = Session()
    # nothing here for now
    session.flush()
    session.commit()

def initialize_sql(engine):
    Session.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    populate()

def initialize_testing_sql(echo = False):
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///:memory:', echo=echo)
    initialize_sql(engine)

if __name__=='__main__':  #pragma: no cover
    initialize_testing_sql()
