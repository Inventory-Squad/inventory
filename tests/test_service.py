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
Inventory API Service Test Suite
Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""

import unittest
import os
import logging
import json
from unittest.mock import patch
from flask_api import status    # HTTP Status Codes
from service.models import Inventory, DataValidationError
from service.service import app, initialize_logging
from inventory_factory import InventoryFactory

######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventoryServer(unittest.TestCase):
    """ Inventory Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.debug = False
        initialize_logging(logging.INFO)
        # app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    # @classmethod
    # def tearDownClass(cls):
    #     pass

    def setUp(self):
        """ Runs before each test """
        Inventory.init_db("test")
        Inventory.remove_all()
        self.app = app.test_client()

    # def tearDown(self):
    #     DB.session.remove()
    #     DB.drop_all()

    def _create_inventories(self, count):
        """ Factory method to create inventory in bulk """
        inventory_list = []
        for _ in range(count):
            test_inventory = InventoryFactory()
            resp = self.app.post('/inventory',
                                 json=test_inventory.serialize(),
                                 content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED,
                             'Could not create test inventory')
            new_inventory = resp.get_json()
            test_inventory.id = new_inventory['_id']
            inventory_list.append(test_inventory)
        return inventory_list

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b'Inventory REST API Service', resp.data)

    def test_health_check(self):
        """ Test the Health Check """
        resp = self.app.get('/healthcheck')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b'Healthy', resp.data)

    def test_disable_inventory(self):
        """ Disable an existing Inventory """
        # create inventories to update
        test_inventory = []
        for _ in range(0, 2):
            test = Inventory(product_id=1, quantity=100, restock_level=20,
                             condition="new", available=True)
            test.save()
            test_inventory.append(test)

        # disable the inventory
        product_id = 1
        resp = self.app.put('/inventory/{}/disable'.format(product_id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        disabled_data = resp.get_json()
        self.assertEqual(len(disabled_data), 2)
        for row in resp.get_json():
            self.assertEqual(row['available'], False)

        # test disabling an inventory with wrong product_id
        wrong_product_id = 2
        resp = self.app.put('/inventory/{}/disable'.format(wrong_product_id),
                            content_type='application/json')
        disabled_data = resp.get_json()
        self.assertEqual(len(disabled_data), 0)

    def test_create_inventory(self):
        """ Create a new Inventory """
        test_inventory = InventoryFactory()
        resp = self.app.post('/inventory',
                             json=test_inventory.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_inventory = resp.get_json()
        self.assertEqual(new_inventory['product_id'],
                         test_inventory.product_id,
                         "product_id do not match")
        self.assertEqual(new_inventory['quantity'],
                         test_inventory.quantity,
                         "quantity do not match")
        self.assertEqual(new_inventory['restock_level'],
                         test_inventory.restock_level,
                         "restock_level does not match")
        self.assertEqual(new_inventory['condition'],
                         test_inventory.condition,
                         "condition does not match")
        self.assertEqual(new_inventory['available'],
                         test_inventory.available,
                         "available does not match")
        # Check that the location header was correct
        resp = self.app.get(location,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_inventory = resp.get_json()
        self.assertEqual(new_inventory['product_id'],
                         test_inventory.product_id,
                         "product_id do not match")
        self.assertEqual(new_inventory['quantity'],
                         test_inventory.quantity,
                         "quantity do not match")
        self.assertEqual(new_inventory['restock_level'],
                         test_inventory.restock_level,
                         "restock_level does not match")
        self.assertEqual(new_inventory['condition'],
                         test_inventory.condition,
                         "condition does not match")
        self.assertEqual(new_inventory['available'],
                         test_inventory.available,
                         "available does not match")

    def test_create_inventory_with_bad_data(self):
        """ Create with wrong type"""
        test_inventory = Inventory(product_id=1, quantity=30, restock_level=20,
                                   condition='new', available="True")
        resp = self.app.post('/inventory',
                             json=test_inventory.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_inventory_list(self):
        """ Get a list of Inventory """
        self._create_inventories(5)
        resp = self.app.get('/inventory')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_inventory(self):
        """ Get a single Inventory """
        test_inventory = self._create_inventories(1)[0]
        resp = self.app.get('/inventory/{}'
                            .format(test_inventory.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['product_id'], test_inventory.product_id)

    def test_get_inventory_not_found(self):
        """ Get an Inventory thats not found """
        resp = self.app.get('/inventory/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_inventory_list_by_product_id(self):
        """ Query an Inventory by product id """
        inventories = []
        inventories = self._create_inventories(5)
        test_product_id = inventories[0].product_id
        product_id = [
            i for i in inventories if i.product_id == test_product_id]
        resp = self.app.get('/inventory',
                            query_string='product-id={}'
                            .format(test_product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(product_id))
        for inventory in data:
            self.assertEqual(inventory['product_id'], test_product_id)

    def test_query_inventory_list_by_restock(self):
        """ Query Inventories if quatity is lower than restock_level """
        inventories = []
        for _ in range(5):
            test = Inventory(product_id=_, quantity=_, restock_level=3,
                             condition="new", available=True)
            test.save()
            inventories.append(test)
        resp = self.app.get('/inventory',
                            query_string='restock=true')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 3)
        resp = self.app.get('/inventory',
                            query_string='restock=false')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_query_inventory_list_by_restock_level(self):
        """ Query Inventories by restock_level """
        inventories = []
        for _ in range(0, 2):
            test = Inventory(product_id=_, quantity=_, restock_level=20,
                             condition="new", available=True)
            test.save()
            inventories.append(test)
        for _ in range(2, 5):
            test = Inventory(product_id=_, quantity=_, restock_level=50,
                             condition="new", available=True)
            test.save()
            inventories.append(test)
        resp = self.app.get('/inventory',
                            query_string='restock-level={}'.format(20))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)
        resp = self.app.get('/inventory',
                            query_string='restock-level={}'.format(50))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 3)

    def test_query_by_condition(self):
        """ Query an Inventory by Condition """
        inventories = []
        for _ in range(1, 3):
            test = Inventory(product_id=_, quantity=_, restock_level=20,
                             condition='new', available=True)
            test.save()
            inventories.append(test)
        for _ in range(1, 3):
            test = Inventory(product_id=_, quantity=_, restock_level=20,
                             condition='used', available=True)
            test.save()
            inventories.append(test)
        # inventories = self._create_inventories(5)
        test_condition = inventories[0].condition
        test_pid = inventories[0].product_id
        condition_inventories = [
            i for i in inventories if i.condition == test_condition]
        pid_condition_inventories = [i for i in inventories if (
            i.condition == test_condition and i.product_id == test_pid)]
        # /inventory?condition={condition}
        resp = self.app.get('/inventory?condition={}'.format(test_condition))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(condition_inventories))
        for i in data:
            self.assertEqual(i['condition'], test_condition)
        # /inventory?product-id={pid}&condition={condition}
        resp = self.app.get('/inventory',
                            query_string='product-id={0}&condition={1}'.format(
                                test_pid, test_condition))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(pid_condition_inventories))
        for i in data:
            self.assertEqual(i['condition'], test_condition)
            self.assertEqual(i['product_id'], test_pid)

    def test_query_inventory_list_by_availability(self):
        """ Query an Inventory by availability """
        inventories = []
        test = Inventory(product_id=1, quantity=30, restock_level=20,
                             condition='new', available=True)
        test.save()
        inventories.append(test)
        test = Inventory(product_id=2, quantity=30, restock_level=20,
                             condition='used', available=False)
        test.save()
        inventories.append(test)
        for _ in range(0, 3):
            test = Inventory(product_id=_, quantity=30, restock_level=20,
                             condition='new', available=True)
            test.save()
            inventories.append(test)
        for _ in range(1, 5):
            test = Inventory(product_id=_, quantity=30, restock_level=50,
                             condition='new', available=False)
            test.save()
            inventories.append(test)
        # /inventory?available={availability} 
        resp = self.app.get('/inventory',
                            query_string='available=true')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 4)
        for inventory in data:
            self.assertEqual(inventory['available'], True)
        resp = self.app.get('/inventory',
                            query_string='available=false')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)
        for inventory in data:
            self.assertEqual(inventory['available'], False)
        # /inventory?product-id={pid}&available={availability}
        resp = self.app.get('/inventory',
                            query_string='product-id=1&available=true')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)
        for inventory in data:
            self.assertEqual(inventory['product_id'], 1)
            self.assertEqual(inventory['available'], True)
        resp = self.app.get('/inventory',
                            query_string='product-id=2&available=false')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)
        for inventory in data:
            self.assertEqual(inventory['product_id'], 2)
            self.assertEqual(inventory['available'], False)       

    def test_update_inventory(self):
        """ Update an existing Inventory """
        test_inventory = {"product_id": 2,
                          "quantity": 100,
                          "restock_level": 40,
                          "condition": 'new',
                          "available": True}
        resp = self.app.post('/inventory',
                             json=test_inventory,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        inventory = resp.get_json()
        self.assertEqual(inventory['condition'], 'new')
        self.assertNotEqual(inventory['_id'], None)
        inventory['condition'] = 'used'
        resp = self.app.put('/inventory/{}'.format(inventory['_id']),
                            json=inventory,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # get the inventory again
        resp = self.app.get(
            '/inventory/{}'.format(inventory['_id']),
            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_inventory = resp.get_json()
        self.assertEqual(updated_inventory['condition'], 'used')
        # test updating an inventory with wrong id
        wrong_id = 2
        resp = self.app.put('/inventory/{}'.format(wrong_id),
                            json=inventory,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_inventory(self):
        """ Delete an inventory """
        inventory = self._create_inventories(2)[0]
        count_before_delete = self.get_inventory_count()
        resp = self.app.delete('/inventory/{}'.format(inventory.id),
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        count_after_delete = self.get_inventory_count()
        self.assertEqual(count_after_delete, count_before_delete - 1)

    def test_reset_inventory(self):
        """ Reset inventory """
        resp = self.app.delete('/inventory/reset')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    ####  Mock data #####
    @patch('service.models.Inventory.find_by_condition')
    def test_bad_request(self, bad_request_mock):
        """ Test a bad request error from find_by_condition """
        bad_request_mock.side_effect = DataValidationError()
        resp = self.app.get('/inventory', query_string='condition=wrong')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bad_content_type(self):
        """ Bad content type return 415 """
        test_inventory = InventoryFactory()
        resp = self.app.post('/inventory',
                             json=test_inventory.serialize(),
                             content_type='text/html')
        self.assertEqual(resp.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_db_connection(self):
        """ Test DB connection """
        Inventory.disconnect()
        inventory = InventoryFactory()
        resp = self.app.post('/inventory', data=json.dumps(dict(
            product_id=inventory.product_id,
            quantity=inventory.quantity,
            restock_level=inventory.restock_level,
            condition=inventory.condition,
            available=inventory.available
        )), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        Inventory.connect()
        resp = self.app.post('/inventory', data=json.dumps(dict(
            product_id=inventory.product_id,
            quantity=inventory.quantity,
            restock_level=inventory.restock_level,
            condition=inventory.condition,
            available=inventory.available
        )), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

######################################################################
# Utility functions
######################################################################

    def get_inventory_count(self):
        """ save the current number of invnetory """
        resp = self.app.get('/inventory')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        return len(data)