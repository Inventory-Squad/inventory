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
from service.models import Inventory, DataValidationError
from service import app

######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventory(unittest.TestCase):
    """ Test Cases for Inventory """

    @classmethod
    def setUpClass(cls):
        """ These run once per Test suite """
        app.debug = False

    def setUp(self):
        """ Runs before each test """
        Inventory.init_db("test")
        Inventory.remove_all()

    def test_create_an_inventory(self):
        """ Create an inventory and assert that it exists """
        inventory = Inventory(product_id=1, quantity=100,\
                              restock_level=50, condition="new",\
                              available=True)
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.id, None)
        self.assertEqual(inventory.product_id, 1)
        self.assertEqual(inventory.quantity, 100)
        self.assertEqual(inventory.restock_level, 50)
        self.assertEqual(inventory.condition, 'new')
        self.assertEqual(inventory.available, True)

    def test_create_an_inventory_bad_data(self):
        """ Create an inventory with bad data  """
        inventory_no_product_id = Inventory(quantity=100,\
                                            restock_level=50, condition="new",\
                                            available=True)
        with self.assertRaises(DataValidationError) as error:
            inventory_no_product_id.save()
        self.assertEqual(str(error.exception), 'product_id is not set')

        inventory_no_quantity = Inventory(product_id=1,\
                                          restock_level=50, condition="new",\
                                          available=True)
        with self.assertRaises(DataValidationError) as error:
            inventory_no_quantity.save()
        self.assertEqual(str(error.exception), 'quantity is not set')

        inventory_no_restock_level = Inventory(product_id=1, quantity=100,\
                                               condition="new", available=True)
        with self.assertRaises(DataValidationError) as error:
            inventory_no_restock_level.save()
        self.assertEqual(str(error.exception), 'restock_level is not set')

        inventory_no_condition = Inventory(product_id=1, quantity=100,\
                                            restock_level=50, available=True)
        with self.assertRaises(DataValidationError) as error:
            inventory_no_condition.save()
        self.assertEqual(str(error.exception), 'condition is not set to new/open_box/used')

    def test_add_an_inventory(self):
        """ Create an inventory and add it to the database """
        inventory = Inventory.all()
        self.assertEqual(inventory, [])
        inventory = Inventory(product_id=1, quantity=100,\
                              restock_level=50, condition="new",\
                              available=True)
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.id, None)
        inventory.save()
        inventory = Inventory.all()
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0].quantity, 100)
        self.assertEqual(inventory[0].restock_level, 50)
        self.assertEqual(inventory[0].condition, "new")
        self.assertEqual(inventory[0].available, True)

    def test_update_inventory(self):
        """ Update an existing inventory """
        inventory = Inventory(product_id=1, quantity=100,
                              restock_level=50, condition="new",
                              available=True)
        inventory.save()
        self.assertNotEqual(inventory.id, None)
        # Change it and save it
        inventory.product_id = 2
        inventory.quantity = 200
        inventory.restock_level = 100
        inventory.condition = "used"
        inventory.available = False
        inventory.save()
        # Fetch it back and make sure the id hasn't change
        # but the data did change
        inventory = Inventory.all()
        self.assertEqual(len(inventory), 1)
        self.assertNotEqual(inventory[0].id, None)
        self.assertEqual(inventory[0].product_id, 2)
        self.assertEqual(inventory[0].quantity, 200)
        self.assertEqual(inventory[0].restock_level, 100)
        self.assertEqual(inventory[0].condition, 'used')
        self.assertEqual(inventory[0].available, False)

    def test_update_nonexist(self):
        """ Test updating a nonexist inventory"""
        inventory = Inventory(product_id=1, quantity=100,
                              restock_level=50, condition="new",
                              available=True)
        inventory.id = '1cak41-nonexist'
        try:
            inventory.update()
        except KeyError:
            self.assertRaises(KeyError)

    def test_delete_nonexist(self):
        """ Test deleting a nonexist inventory"""
        inventory = Inventory(product_id=1, quantity=100,
                              restock_level=50, condition="new",
                              available=True)
        inventory.id = '1cak41-nonexist'
        try:
            inventory.delete()
        except KeyError:
            self.assertRaises(KeyError)

    def test_disable_an_inventory(self):
        """ Disable an existing product """
        inventory = Inventory(product_id=1, quantity=100,
                              restock_level=50, condition="new",\
                              available=True)
        inventory.save()
        self.assertEqual(inventory.available, True)
        # Change the status and save it
        inventory.available = False
        inventory.save()

        # Fetch it back and make sure the data did change
        inventory = Inventory.all()
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0].available, False)

    def test_delete_an_inventory_with_id(self):
        """ Delete an inventory """
        inventory = Inventory(product_id=1, quantity=100,
                              restock_level=50, condition="new",
                              available=True)
        inventory.save()
        self.assertEqual(len(Inventory.all()), 1)

        # delete the inventory and make sure it isn't in the database
        inventory.delete()
        self.assertEqual(len(Inventory.all()), 0)

    def test_find_by_restock(self):
        """ Find inventories if quantity lower than their restock level """
        Inventory(product_id=1, quantity=100, restock_level=50,
                  condition="new", available=True).save()
        Inventory(product_id=2, quantity=20, restock_level=50,
                  condition="new", available=True).save()
        Inventory(product_id=3, quantity=30, restock_level=50,
                  condition="new", available=True).save()
        Inventory(product_id=4, quantity=120, restock_level=50,
                  condition="new", available=True).save()
        Inventory(product_id=5, quantity=49, restock_level=50,
                  condition="new", available=True).save()
        inventory = Inventory.find_by_restock(True)
        self.assertEqual(len(inventory), 3)
        inventory = Inventory.find_by_restock(False)
        self.assertEqual(len(inventory), 2)

    def test_find_by_restock_level(self):
        """ Find inventories by restock_level"""
        Inventory(product_id=1, quantity=100, restock_level=20,
                  condition="new", available=True).save()
        Inventory(product_id=2, quantity=20, restock_level=30,
                  condition="new", available=True).save()
        Inventory(product_id=3, quantity=30, restock_level=50,
                  condition="new", available=True).save()
        Inventory(product_id=4, quantity=120, restock_level=50,
                  condition="new", available=True).save()
        Inventory(product_id=5, quantity=49, restock_level=50,
                  condition="new", available=True).save()
        inventory = Inventory.find_by_restock_level(20)
        self.assertEqual(len(inventory), 1)
        inventory = Inventory.find_by_restock_level(50)
        self.assertEqual(len(inventory), 3)

    def test_serialize_an_inventory(self):
        """ Test serialization of an inventory """
        inventory = Inventory(product_id=1, quantity=100,\
                              restock_level=50, condition="new",\
                              available=True)
        data = inventory.serialize()
        self.assertNotEqual(inventory, None)
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
        data = {"id": 1, "product_id":100, "quantity": 100,\
                "restock_level":50, "condition": "new", "available": True}
        inventory = Inventory()
        inventory.deserialize(data)
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.id, None)
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
                         ' of request contained '\
                         'bad or no data : string indices must be integers')

    def test_deserialize_wrong_type_data(self):
        """ Test deserialization of wrong type data """
        inventory = Inventory()
        product_id_boolean = {"id": 1, "product_id": True,\
                              "quantity": 100, "restock_level":50,
                              "condition": "new", "available": True}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(product_id_boolean)
        self.assertEqual(str(error.exception), 'Invalid Inventory: body'\
                         ' of request contained '\
                         'bad or no data : product_id required int')

        product_id_string = {"id": 1, "product_id":"100",\
                             "quantity": 100, "restock_level":50,
                             "condition": "new", "available": True}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(product_id_string)
        self.assertEqual(str(error.exception), 'Invalid Inventory: body'\
                         ' of request contained '\
                         'bad or no data : product_id required int')

        quantity_boolean = {"id": 1, "product_id":100,\
                            "quantity": True, "restock_level":50,\
                            "condition": "new", "available": True}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(quantity_boolean)
        self.assertEqual(str(error.exception), 'Invalid Inventory: body'\
                         ' of request contained '\
                         'bad or no data : quantity required int')

        quantity_string = {"id": 1, "product_id":100,\
                           "quantity": "100", "restock_level":50,\
                           "condition": "new", "available": True}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(quantity_string)
        self.assertEqual(str(error.exception), 'Invalid Inventory: body'\
                         ' of request contained '\
                         'bad or no data : quantity required int')

        restock_level_bool = {"id": 1, "product_id":100,\
                              "quantity": 100, "restock_level": True,
                              "condition": "new", "available": True}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(restock_level_bool)
        self.assertEqual(str(error.exception), 'Invalid Inventory: body'\
                         ' of request contained '\
                         'bad or no data : restock_level required int')

        restock_level_string = {"id": 1, "product_id":100,\
                                "quantity": 100, "restock_level":"50",
                                "condition": "new", "available": True}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(restock_level_string)
        self.assertEqual(str(error.exception), 'Invalid Inventory: body'\
                         ' of request contained '\
                         'bad or no data : restock_level required int')

        condition_int = {"id": 1, "product_id":100,\
                         "quantity": 100, "restock_level": 50,
                         "condition": 1, "available": True}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(condition_int)
        self.assertEqual(str(error.exception), 'Invalid Inventory: body'\
                         ' of request contained '\
                         'bad or no data : condition required string')

        available_int = {"id": 1, "product_id":100,\
                         "quantity": 100, "restock_level":50,
                         "condition": "new", "available": 1}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(available_int)
        self.assertEqual(str(error.exception), 'Invalid Inventory: '\
                         'body of request contained '\
                         'bad or no data : available required bool')

        available_string = {"id": 1, "product_id":100,\
                            "quantity": 100, "restock_level":50,
                            "condition": "new", "available": "true"}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(available_string)
        self.assertEqual(str(error.exception), 'Invalid Inventory: '\
                         'body of request contained '\
                         'bad or no data : available required bool')

    def test_deserialize_missing_data(self):
        """ Test deserialization of missing data """
        inventory = Inventory()
        miss_product_id = {"quantity": 100, "restock_level":50,\
                           "condition": "new", "available": True}
        with self.assertRaises(DataValidationError) as error:
            inventory.deserialize(miss_product_id)
        self.assertEqual(str(error.exception), 'Invalid Inventory: '\
                         'missing product_id')

    def test_find_an_inventory(self):
        """ Find an inventory by id """
        new_inventory = Inventory(product_id=1, quantity=100, restock_level=50,
                                  condition="new", available=True)
        used_inventory = Inventory(product_id=2, quantity=21, restock_level=20,
                                   condition="used", available=True)
        new_inventory.save()
        used_inventory.save()
        inventory = Inventory.find(used_inventory.id)
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.product_id, 2)
        self.assertEqual(inventory.quantity, 21)
        self.assertEqual(inventory.restock_level, 20)
        self.assertEqual(inventory.condition, "used")
        self.assertEqual(inventory.available, True)

    def test_find_an_inventory_by_product_id(self):
        """ Find an inventory by product_id """
        Inventory(product_id=1, quantity=100, restock_level=50,
                  condition="new", available=True).save()
        Inventory(product_id=2, quantity=21, restock_level=20,
                  condition="used", available=True).save()
        inventory = Inventory.find_by_product_id(2)
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0].product_id, 2)
        self.assertEqual(inventory[0].quantity, 21)
        self.assertEqual(inventory[0].restock_level, 20)
        self.assertEqual(inventory[0].condition, "used")
        self.assertEqual(inventory[0].available, True)

    def test_find_by_condition(self):
        """ Find an Inventory by its condition """
        Inventory(product_id=1, quantity=100,
                  restock_level=50, condition="new", available=True).save()
        Inventory(product_id=2, quantity=100,
                  restock_level=50, condition="new", available=True).save()
        Inventory(product_id=3, quantity=80,
                  restock_level=20, condition="used", available=True).save()
        inventory = Inventory.find_by_condition("new")
        self.assertEqual(len(inventory), 2)
        inventory = Inventory.find_by_condition_with_pid('new', 1)
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0].product_id, 1)
        self.assertEqual(inventory[0].quantity, 100)
        self.assertEqual(inventory[0].restock_level, 50)
        self.assertEqual(inventory[0].condition, 'new')
        self.assertEqual(inventory[0].available, True)

    def test_find_an_inventory_by_availability(self):
        """ Find an inventory by availability """
        Inventory(product_id=1, quantity=100, restock_level=50,
                  condition="new", available=False).save()
        Inventory(product_id=2, quantity=21, restock_level=20,
                  condition="used", available=True).save()
        inventory = Inventory.find_by_availability(True)
        self.assertEqual(len(inventory), 1)
        self.assertEqual(inventory[0].product_id, 2)
        self.assertEqual(inventory[0].quantity, 21)
        self.assertEqual(inventory[0].restock_level, 20)
        self.assertEqual(inventory[0].condition, "used")
        self.assertEqual(inventory[0].available, True)

    def test_find(self):
        """ Find a Inventory by ID """
        Inventory(product_id=1, quantity=100, restock_level=50,
                  condition="new", available=False).save()
        inventory = Inventory(product_id=2, quantity=21, restock_level=20,
                  condition="used", available=True)
        inventory.save()

        res = Inventory.find(inventory.id)
        self.assertIsNot(res, None)
        self.assertEqual(res.product_id, inventory.product_id)
        self.assertEqual(res.quantity, inventory.quantity)
        self.assertEqual(res.condition, inventory.condition)
        self.assertEqual(res.available, inventory.available)
        self.assertEqual(res.id, inventory.id)
