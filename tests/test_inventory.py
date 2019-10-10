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
from service.models import Inventory, DataValidationError, db
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
        inventory = Inventory(product_id=1, quantity=100, restock_level\
                              =50, condition="new", available=True)
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.inventory_id, None)
        self.assertEqual(inventory.product_id, 1)
        self.assertEqual(inventory.quantity, 100)
        self.assertEqual(inventory.restock_level, 50)
        self.assertEqual(inventory.condition, 'new')
        self.assertEqual(inventory.available, True)

    def test_add_an_inventory(self):
        """ Create an inventory and add it to the database """
        inventory = Inventory.all()
        self.assertEqual(inventory, [])
        inventory = Inventory(product_id=1, quantity=100, restock_level\
                              =50, condition="new", available=True)
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.inventory_id, None)
        inventory.save()
        self.assertEqual(inventory.inventory_id, 1)
        inventory = Inventory.all()
        self.assertEqual(len(inventory), 1)

    def test_disable_an_inventory(self):
        """ Disable an existing product """
        inventory = Inventory(product_id=1, quantity=100,
                              restock_level=50, condition="new", \
                              available=True)
        inventory.save()
        self.assertEqual(inventory.inventory_id, 1)

        # Change the status and save it
        inventory.available = False
        inventory.save()

        # Fetch it back and make sure the data did change
        inventory = Inventory.all()
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0].available, False)

    def test_delete_an_inventory_with_inventory_id(self):
        """ Delete an inventory """
        inventory = Inventory(product_id=1, available=True)
        inventory.save()
        self.assertEqual(len(Inventory.all()), 1)

        # delete the inventory and make sure it isn't in the database
        inventory.delete()
        self.assertEqual(len(Inventory.all()), 0)

    def test_serialize_an_inventory(self):
        """ Test serialization of an inventory """
        inventory = Inventory(product_id=1, quantity=100, restock_level\
                              =50, condition="new", available=True)
        data = inventory.serialize()
        self.assertNotEqual(inventory, None)
        self.assertIn('inventory_id', data)
        self.assertEqual(data['inventory_id'], None)
        self.assertIn('product_id', data)
        self.assertEqual(data['product_id'], 1)
        self.assertIn('quantity', data)
        self.assertEqual(data['quantity'], 100)
        self.assertIn('restock_level', data)
        self.assertEqual(data['restock_level'], 50)
        self.assertIn('condition', data)
        self.assertEqual(data['condition'], "new")
        self.assertIn('available', data)
        self.assertEqual(data['available'], True)

    def test_deserialize_an_inventory(self):
        """ Test deserialization of an inventory """
        data = {"inventory_id": 1, "product_id":100, "quantity": 100, \
                "restock_level":50,
                "condition": "new", "available": True}
        inventory = Inventory()
        inventory.deserialize(data)
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.inventory_id, None)
        self.assertEqual(inventory.product_id, 100)
        self.assertEqual(inventory.quantity, 100)
        self.assertEqual(inventory.restock_level, 50)
        self.assertEqual(inventory.condition, "new")
        self.assertEqual(inventory.available, True)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        inventory = Inventory()
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(data)
        self.assertEqual(str(error.exception), 'Invalid Inventory: body'\
                         ' of request contained ' \
                         'bad or no data : string indices must be integers')

    def test_deserialize_wrong_type_data(self):
        """ Test deserialization of wrong type data """
        inventory = Inventory()
        product_id_string = {"inventory_id": 1, "product_id":"100", \
                             "quantity": 100, "restock_level":50,
                             "condition": "new", "available": True}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(product_id_string)
        self.assertEqual(str(error.exception), 'Invalid Inventory: body'\
                         ' of request contained ' \
                         'bad or no data : product_id required int')

        quantity_string = {"inventory_id": 1, "product_id":100, "quantity"\
                           : "100", "restock_level":50,
                           "condition": "new", "available": True}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(quantity_string)
        self.assertEqual(str(error.exception), 'Invalid Inventory: body'\
                         ' of request contained ' \
                         'bad or no data : quantity required int')

        restock_level_string = {"inventory_id": 1, "product_id":100, \
                                "quantity": 100, "restock_level":"50",
                                "condition": "new", "available": True}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(restock_level_string)
        self.assertEqual(str(error.exception), 'Invalid Inventory: body'\
                         ' of request contained ' \
                         'bad or no data : restock_level required int')

        condition_int = {"inventory_id": 1, "product_id":100, "quantity"\
                         : 100, "restock_level": 50,
                         "condition": 1, "available": True}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(condition_int)
        self.assertEqual(str(error.exception), 'Invalid Inventory: body'\
                         ' of request contained ' \
                         'bad or no data : condition required string')

        available_string = {"inventory_id": 1, "product_id":100, \
                            "quantity": 100, "restock_level":50,
                            "condition": "new", "available": "true"}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(available_string)
        self.assertEqual(str(error.exception), 'Invalid Inventory: '\
                         'body of request contained ' \
                         'bad or no data : available required bool')

    def test_deserialize_missing_data(self):
        """ Test deserialization of missing data """
        inventory = Inventory()
        miss_product_id = {"quantity": 100, "restock_level":"50", \
                           "condition": "new", "available": "true"}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(miss_product_id)
        self.assertEqual(str(error.exception), 'Invalid Inventory: '\
                         'missing product_id')
