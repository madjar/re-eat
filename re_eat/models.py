#!/usr/bin/env python
# -*- coding: Utf-8 -*-

import logging
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, scoped_session

logger = logging.getLogger(__name__)

Base = declarative_base()
Session = scoped_session(sessionmaker(autocommit=True))

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

    def __repr__(self):  # pragma: no cover
        return '<Recipe: "%s">' % self.name


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):  # pragma: no cover
        return '<Tag: "%s">' % self.name

    @classmethod
    def get(cls, name):
        tag = Session.query(Tag).filter_by(name=name).first()
        if not tag:
            tag = Tag(name)
            Session.add(tag)
        return tag


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

    def __repr__(self):  # pragma: no cover
        return '<Meal: %s, %s, %s>' % (self.date, self.index, self.recipes)


def initialize_sql(url='sqlite:///:memory:', echo=True):
    engine = create_engine(url, echo=echo)
    Session.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
if __name__ == '__main__':  # pragma: no cover
    initialize_sql()
