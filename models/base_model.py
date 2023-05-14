#!/usr/bin/python3
"""Defines all the common attributes/methods for other classes
"""
import uuid
from datetime import datetime
import models


class BaseModel:
    """Base class for all models"""

    def __init__(self, *args, **kwargs):
        """Initialization of the Base instance.
        Args:
            - *args: list of arguments
            - **kwargs: dict of key-values arguments
        """
        if kwargs:
            dtime_format = '%Y-%m-%dT%H:%M:%S.%f'
            for key, value in kwargs.items():
                if key == '__class__':
                    continue
                elif key == 'created_at':
                    self.created_at = datetime.strptime(
                        kwargs['created_at'], dtime_format)
                elif key == 'updated_at':
                    self.updated_at = datetime.strptime(
                        kwargs['updated_at'], dtime_format)
                else:
                    setattr(self, key, value)
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.now()
            self.updated_at = datetime.now()
            models.storage.new(self)  # as instructed also in task 5

    def __str__(self):
        """Returns a readable  the string representation
        of BaseModel instances"""

        clsName = self.__class__.__name__
        return "[{}] ({}) {}".format(clsName, self.id, self.__dict__)

    def save(self):
        """Updates the public instance attribute updated_at
        with the current datetime"""

        self.updated_at = datetime.now()
        models.storage.save()

    def to_dict(self):
        """Returns a dictionary that contains all
        keys/values of the instance"""
        my_dict = self.__dict__.copy()
        my_dict['updated_at'] = self.updated_at.isoformat()
        my_dict['created_at'] = self.created_at.isoformat()
        my_dict['__class__'] = self.__class__.__name__
        # OR
        # my_dict = dict()
        # my_dict['__class__'] = self.__class__.__name__
        # for key, value in self.__dict__.items():
        #    if key in ('created_at', 'updated_at'):
        #        my_dict[key] = value.isoformat()
        #    else:
        #        my_dict[key] = value
        return my_dict
        # my_dict = dict()
        # my_dict['__class__'] = self.__class__.__name__
        # for key, value in self.__dict__.items():
        #    if type(value) is datetime:
        #        my_dict[key] = value.isoformat()
        #    else:
        #        my_dict[key] = value
        # return my_dict
