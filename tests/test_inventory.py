# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for inventory Model

Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
import os
from werkzeug.exceptions import NotFound
from service.models import Inventory, DataValidationError, RequiredFieldError, db
from service import app

DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://root:passw0rd@localhost:3306/mysql')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventory(unittest.TestCase):
    """ Test Cases for Inventory """

    @classmethod
    def setUpClass(cls):
        """ These run once per Test suite """
        app.debug = False
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass
    
    def setUp(self):
        Inventory.init_db(app)
        db.drop_all()    # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_an_inventory(self):
        """ Create an inventory and assert that it exists """
        inventory = Inventory(product_id=1, quantity=100, restock_level=50, condition="new", available=True)
        self.assertTrue(inventory != None)
        self.assertEqual(inventory.inventory_id, None)
        self.assertEqual(inventory.product_id, 1)
        self.assertEqual(inventory.quantity, 100)
        self.assertEqual(inventory.restock_level, 50)
        self.assertEqual(inventory.condition, 'new')
        self.assertEqual(inventory.available, True)

    def test_create_an_inventory_with_bad_product_id_type(self):
        """ Create an inventory with bad product_id type and assert TypeError will raise """
        inventory_with_product_id_as_string = Inventory(product_id="product_id", quantity=100, restock_level=50, condition="new", available=True)
        inventory_with_product_id_as_boolean = Inventory(product_id=False, quantity=100, restock_level=50, condition="new", available=True)
        inventory_with_product_id_as_negative_int = Inventory(product_id=-1, quantity=100, restock_level=50, condition="new", available=True)
        inventory_with_product_id_as_float = Inventory(product_id=1.02, quantity=100, restock_level=50, condition="new", available=True)
        inventory_with_product_id_as_none = Inventory(product_id=None, quantity=100, restock_level=50, condition="new", available=True)
        self.assertRaises(TypeError, Inventory.save, inventory_with_product_id_as_string)
        self.assertRaises(TypeError, Inventory.save, inventory_with_product_id_as_boolean)
        self.assertRaises(TypeError, Inventory.save, inventory_with_product_id_as_negative_int)
        self.assertRaises(TypeError, Inventory.save, inventory_with_product_id_as_float)
        self.assertRaises(TypeError, Inventory.save, inventory_with_product_id_as_none)

    def test_create_an_inventory_with_bad_quantity_type(self):
        """ Create an inventory with bad quantity type and assert TypeError will raise """
        inventory_with_quantity_as_string = Inventory(product_id=1, quantity="quantity", restock_level=50, condition="new", available=True)
        inventory_with_quantity_as_boolean = Inventory(product_id=1, quantity=True, restock_level=50, condition="new", available=True)
        inventory_with_quantity_as_negative_int = Inventory(product_id=1, quantity=-100, restock_level=50, condition="new", available=True)
        inventory_with_quantity_as_float = Inventory(product_id=1, quantity=100.51, restock_level=50, condition="new", available=True)
        inventory_with_quantity_as_none = Inventory(product_id=1, quantity=None, restock_level=50, condition="new", available=True)
        self.assertRaises(TypeError, Inventory.save, inventory_with_quantity_as_string)
        self.assertRaises(TypeError, Inventory.save, inventory_with_quantity_as_boolean)
        self.assertRaises(TypeError, Inventory.save, inventory_with_quantity_as_negative_int)
        self.assertRaises(TypeError, Inventory.save, inventory_with_quantity_as_float)
        self.assertRaises(TypeError, Inventory.save, inventory_with_quantity_as_none)
        

    def test_create_an_inventory_with_bad_restock_level_type(self):
        """ Create an inventory with bad restock_level type and assert TypeError will raise """
        inventory_with_restock_level_as_string = Inventory(product_id=1, quantity=100, restock_level="restock_level", condition="new", available=True)
        inventory_with_restock_level_as_boolean = Inventory(product_id=1, quantity=100, restock_level=True, condition="new", available=True)
        inventory_with_restock_level_as_negative_int = Inventory(product_id=1, quantity=100, restock_level=-1, condition="new", available=True)
        inventory_with_restock_level_as_float = Inventory(product_id=1, quantity=100, restock_level=50.5, condition="new", available=True)
        inventory_with_restock_level_as_none = Inventory(product_id=1, quantity=100, restock_level=None, condition="new", available=True)
        self.assertRaises(TypeError, Inventory.save, inventory_with_restock_level_as_string)
        self.assertRaises(TypeError, Inventory.save, inventory_with_restock_level_as_boolean)
        self.assertRaises(TypeError, Inventory.save, inventory_with_restock_level_as_negative_int)
        self.assertRaises(TypeError, Inventory.save, inventory_with_restock_level_as_float)
        self.assertRaises(TypeError, Inventory.save, inventory_with_restock_level_as_none)

    def test_create_an_inventory_with_bad_condition_type(self):
        """ Create an inventory with bad condition type and assert TypeError will raise """
        inventory_with_condition_as_int = Inventory(product_id=1, quantity=100, restock_level=50, condition=1, available=True)
        inventory_with_condition_as_boolean = Inventory(product_id=1, quantity=100, restock_level=50, condition=True, available=True)
        inventory_with_condition_as_float = Inventory(product_id=1, quantity=100, restock_level=50, condition=1.01, available=True)
        inventory_with_condition_as_none = Inventory(product_id=1, quantity=100, restock_level=50, condition=None, available=True)
        self.assertRaises(TypeError, Inventory.save, inventory_with_condition_as_int)
        self.assertRaises(TypeError, Inventory.save, inventory_with_condition_as_boolean)
        self.assertRaises(TypeError, Inventory.save, inventory_with_condition_as_float)
        self.assertRaises(TypeError, Inventory.save, inventory_with_condition_as_none)

    def test_create_an_inventory_with_bad_available_type(self):
        """ Create an inventory with bad available type and assert TypeError will raise """
        inventory_with_available_as_string = Inventory(product_id=1, quantity=100, restock_level=50, condition="new", available="True")
        inventory_with_available_as_int = Inventory(product_id=1, quantity=100, restock_level=50, condition="new", available=1)
        inventory_with_available_as_float = Inventory(product_id=1, quantity=100, restock_level=50, condition="new", available=0.01)
        inventory_with_available_as_none = Inventory(product_id=1, quantity=100, restock_level=50, condition="new", available=None)
        self.assertRaises(TypeError, Inventory.save, inventory_with_available_as_string)
        self.assertRaises(TypeError, Inventory.save, inventory_with_available_as_int)
        self.assertRaises(TypeError, Inventory.save, inventory_with_available_as_float)
        self.assertRaises(TypeError, Inventory.save, inventory_with_available_as_none)

    def test_create_an_inventory_with_missing_required_field(self):
        """ Create an inventory with missing required field and assert RequiredFieldError will raise """
        inventory_missing_product_id = Inventory(quantity=100, restock_level=50, condition="new", available="True")
        inventory_missing_restock_level = Inventory(product_id=1, quantity=100, condition="new", available="True")
        inventory_missing_quantity = Inventory(product_id=1, restock_level=50, condition="new", available="True")
        inventory_missing_condition = Inventory(product_id=1, restock_level=50, quantity=100, available="True")
        inventory_missing_available = Inventory(product_id=1, restock_level=50, quantity=100, condition="new")
        self.assertRaises(RequiredFieldError, Inventory.save, inventory_missing_product_id)
        self.assertRaises(RequiredFieldError, Inventory.save, inventory_missing_restock_level)
        self.assertRaises(RequiredFieldError, Inventory.save, inventory_missing_quantity)
        self.assertRaises(RequiredFieldError, Inventory.save, inventory_missing_condition)
        self.assertRaises(RequiredFieldError, Inventory.save, inventory_missing_available)

    def test_add_an_inventory(self):
        """ Create an inventory and add it to the database """
        inventory = Inventory.all()
        self.assertEqual(inventory, [])
        inventory = Inventory(product_id=1, quantity=100, restock_level=50, condition="new", available=True)
        self.assertTrue(inventory != None)
        self.assertEqual(inventory.inventory_id, None)
        inventory.save()
        self.assertEqual(inventory.inventory_id, 1)
        inventory = Inventory.all()
        self.assertEqual(len(inventory), 1)


    




