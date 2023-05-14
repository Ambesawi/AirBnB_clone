#!/usr/bin/python3
""" Class user my class"""

from models.base_model import BaseModel


class User(BaseModel):
    """ Class user """
    email = ""
    password = ""
    first_name = ""
    last_name = ""
