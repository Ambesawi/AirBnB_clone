#!/usr/bin/python3
"""Defines unittests for models/base_model.py.
Unittest classes:
    TestBaseModel_instantiation
    TestBase_Instance_Print
    TestBaseModel_save
    TestBase_from_json_string
    TestBaseModel_to_dict
"""
from fileinput import lineno
import unittest
from models import storage
from models.base_model import BaseModel
from models.engine.file_storage import FileStorage
from datetime import datetime
from time import sleep
import time
import uuid
import json
import os
import re

class TestBaseModel_Instantiation(unittest.TestCase):
    """Unittests testing instantiation of the BaseModel class."""

    def test_IsInstanceOf(self):
        """Test instance"""
        b1 = BaseModel()
        self.assertIsInstance(b1, BaseModel)
        self.assertEqual(str(type(b1)), "<class 'models.base_model.BaseModel'>")
        self.assertTrue(issubclass(type(b1), BaseModel))

    def test_ContainsId(self):
        """Test if id attribute exists"""
        b1 = BaseModel()
        self.assertTrue(hasattr(b1, "id"))

    def test_IdType(self):
        """Test if `id` attribute type"""
        b1 = BaseModel()
        self.assertEqual(type(b1.id), str)

    def test_CompareTwoInstancesId(self):
        """Compare distinct instances ids"""
        b1 = BaseModel()
        b2 = BaseModel()
        self.assertNotEqual(b1.id, b2.id)

    def test_uuid(self):
        """Test that id is a valid uuid"""
        b1 = BaseModel()
        b2 = BaseModel()
        for inst in [b1, b2]:
            uuid = inst.id
            with self.subTest(uuid=uuid):
                self.assertIs(type(uuid), str)
                self.assertRegex(uuid,
                                 '^[0-9a-f]{8}-[0-9a-f]{4}'
                                 '-[0-9a-f]{4}-[0-9a-f]{4}'
                                 '-[0-9a-f]{12}$')
        self.assertNotEqual(b1.id, b2.id)

    def test_uniq_id(self):
        """Tests for unique user ids."""
        u = [BaseModel().id for i in range(1000)]
        self.assertEqual(len(set(u)), len(u))

    def test_two_models_unique_ids(self):
        b1 = BaseModel()
        b2 = BaseModel()
        self.assertNotEqual(b1.id, b2.id)

    def test_new_instance_stored_in_objects(self):
        self.assertIn(BaseModel(), storage.all().values())

    def test_ContainsCreated_at(self):
        """Checks `created_at` attribute existence"""
        b1 = BaseModel()
        self.assertTrue(hasattr(b1, "created_at"))

    def test_Created_atInstance(self):
        """Checks `created_at` attribute's type"""
        b1 = BaseModel()
        self.assertIsInstance(b1.created_at, datetime)

    def test_ContainsUpdated_at(self):
        """Checks `updated_at` attribute existence"""
        b1 = BaseModel()
        self.assertTrue(hasattr(b1, "updated_at"))

    def test_Updated_atInstance(self):
        """Check `updated_at` attribute type"""
        b1 = BaseModel()
        self.assertIsInstance(b1.updated_at, datetime)

    def test_datetime_created(self):
        """Tests if updated_at & created_at are current at creation."""
        date_now = datetime.now()
        b1 = BaseModel()
        diff = b1.updated_at - b1.created_at
        self.assertTrue(abs(diff.total_seconds()) < 0.01)
        diff = b1.created_at - date_now
        self.assertTrue(abs(diff.total_seconds()) < 0.1)

    def test_id_is_public_str(self):
        self.assertEqual(str, type(BaseModel().id))

    def test_created_at_is_public_datetime(self):
        self.assertEqual(datetime, type(BaseModel().created_at))

    def test_updated_at_is_public_datetime(self):
        self.assertEqual(datetime, type(BaseModel().updated_at))

    def test_str_representation(self):
        dt = datetime.today()
        dt_repr = repr(dt)
        b1 = BaseModel()
        b1.id = "123456"
        b1.created_at = b1.updated_at = dt
        b1str = b1.__str__()
        self.assertIn("[BaseModel] (123456)", b1str)
        self.assertIn("'id': '123456'", b1str)
        self.assertIn("'created_at': " + dt_repr, b1str)
        self.assertIn("'updated_at': " + dt_repr, b1str)

    def test_args_unused(self):
        b1 = BaseModel(None)
        self.assertNotIn(None, b1.__dict__.values())

    def test_instantiation_with_kwargs(self):
        dt = datetime.today()
        dt_iso = dt.isoformat()
        b1 = BaseModel(id="345", created_at=dt_iso, updated_at=dt_iso)
        self.assertEqual(b1.id, "345")
        self.assertEqual(b1.created_at, dt)
        self.assertEqual(b1.updated_at, dt)

    def test_instantiation_with_None_kwargs(self):
        with self.assertRaises(TypeError):
            BaseModel(id=None, created_at=None, updated_at=None)

    def test_instantiation_with_args_and_kwargs(self):
        dt = datetime.today()
        dt_iso = dt.isoformat()
        b1 = BaseModel("12", id="345", created_at=dt_iso, updated_at=dt_iso)
        self.assertEqual(b1.id, "345")
        self.assertEqual(b1.created_at, dt)
        self.assertEqual(b1.updated_at, dt)

class TestBaseModel_Instance_Print(unittest.TestCase):
    """Unittest for testing the __str__ method."""

    def test_str_return(self):
        """Unittest for testing the return value of __str__ method."""
        b1 = BaseModel()
        Dika = "[{}] ({}) {}".format("BaseModel", b1.id, str(b1.__dict__))
        self.assertEqual(str(b1), Dika)

    def test_str(self):
        """test that the str method has the correct output"""
        b1 = BaseModel()
        string = "[BaseModel] ({}) {}".format(b1.id, b1.__dict__)
        self.assertEqual(string, str(b1))

    def test_of_str(self):
        """Tests for __str__ method."""
        b1 = BaseModel()
        rex = re.compile(r"^\[(.*)\] \((.*)\) (.*)$")
        res = rex.match(str(b1))
        self.assertIsNotNone(res)
        self.assertEqual(res.group(1), "BaseModel")
        self.assertEqual(res.group(2), b1.id)
        s = res.group(3)
        s = re.sub(r"(datetime\.datetime\([^)]*\))", "'\\1'", s)
        d = json.loads(s.replace("'", '"'))
        d2 = b1.__dict__.copy()
        d2["created_at"] = repr(d2["created_at"])
        d2["updated_at"] = repr(d2["updated_at"])
        self.assertEqual(d, d2)

class TestBaseModel_Save_Method(unittest.TestCase):
    """Unittest for testing the save method."""

    def test_validates_save(self):
        """Check save models"""
        b1 = BaseModel()
        updated_at_1 = b1.updated_at
        b1.save()
        updated_at_2 = b1.updated_at
        self.assertNotEqual(updated_at_1, updated_at_2)

    def test_one_save(self):
        b1 = BaseModel()
        sleep(0.05)
        first_updated_at = b1.updated_at
        b1.save()
        self.assertLess(first_updated_at, b1.updated_at)

    def test_two_saves(self):
        b1 = BaseModel()
        sleep(0.05)
        first_updated_at = b1.updated_at
        b1.save()
        second_updated_at = b1.updated_at
        self.assertLess(first_updated_at, second_updated_at)
        sleep(0.05)
        b1.save()
        self.assertLess(second_updated_at, b1.updated_at)

    def test_save_with_arg(self):
        b1 = BaseModel()
        with self.assertRaises(TypeError):
            b1.save(None)

class TestBaseModel_to_Dict_Method(unittest.TestCase):
    """Unittest for testing the to_dict method of the BaseModel class."""

    def test_className_present(self):
        """Test className present"""
        b1 = BaseModel()
        dic = b1.to_dict()
        self.assertNotEqual(dic, b1.__dict__)

    def test_attribute_ISO_format(self):
        """Test datetime field isoformated"""
        b1 = BaseModel()
        dic = b1.to_dict()
        self.assertEqual(type(dic['created_at']), str)
        self.assertEqual(type(dic['updated_at']), str)

    def test_to_dict_type(self):
        b1 = BaseModel()
        self.assertTrue(dict, type(b1.to_dict()))

    def test_to_dict_contains_correct_keys(self):
        b1 = BaseModel()
        self.assertIn("id", b1.to_dict())
        self.assertIn("created_at", b1.to_dict())
        self.assertIn("updated_at", b1.to_dict())
        self.assertIn("__class__", b1.to_dict())

    def test_to_dict_contains_added_attributes(self):
        b1 = BaseModel()
        b1.name = "Holberton"
        b1.my_number = 98
        self.assertIn("name", b1.to_dict())
        self.assertIn("my_number", b1.to_dict())

    def test_to_dict_datetime_attributes_are_strs(self):
        b1 = BaseModel()
        b1_dict = b1.to_dict()
        self.assertEqual(str, type(b1_dict["created_at"]))
        self.assertEqual(str, type(b1_dict["updated_at"]))

    def test_to_dict_output(self):
        dt = datetime.today()
        b1 = BaseModel()
        b1.id = "123456"
        b1.created_at = b1.updated_at = dt
        tdict = {
            'id': '123456',
            '__class__': 'BaseModel',
            'created_at': dt.isoformat(),
            'updated_at': dt.isoformat()
        }
        self.assertDictEqual(b1.to_dict(), tdict)

    def test_contrast_to_dict_dunder_dict(self):
        b1 = BaseModel()
        self.assertNotEqual(b1.to_dict(), b1.__dict__)

    def test_to_dict_with_arg(self):
        b1 = BaseModel()
        with self.assertRaises(TypeError):
            b1.to_dict(None)


if __name__ == "__main__":
    unittest.main()
