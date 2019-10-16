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
from unittest.mock import patch
from flask_api import status    # HTTP Status Codes
from service.models import DB, Inventory, DataValidationError
from service.service import app, init_db, initialize_logging, \
internal_server_error
from tests.inventory_factory import InventoryFactory

DATABASE_URI = os.getenv('DATABASE_URI',
                         'mysql+pymysql://root:passw0rd@localhost:3306/mysql')

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
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        init_db()
        DB.drop_all()
        DB.create_all()
        self.app = app.test_client()

    def tearDown(self):
        DB.session.remove()
        DB.drop_all()

    @classmethod
    def _create_inventories(cls, count):
        """ Factory method to create inventory in bulk """
        lists = []
        for _ in range(count):
            test = Inventory(product_id=_, quantity=100, restock_level=50,
                             condition="new", available=True)
            test.save()
            lists.append(test)
        return lists

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], 'Inventory REST API Service')

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
        resp = self.app.put('/inventory/disable/{}'.format(product_id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        disabled_data = resp.get_json()
        self.assertEqual(len(disabled_data), 2)
        for row in resp.get_json():
            self.assertEqual(row['available'], False)

        # test disabling an inventory with wrong product_id
        wrong_product_id = 2
        resp = self.app.put('/inventory/disable/{}'.format(wrong_product_id),
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
                            .format(test_inventory.inventory_id),
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
        resp = self.app.get('/inventory',
                            query_string='product-id={}'
                            .format(test_product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        for inventory in data:
            self.assertEqual(inventory['product_id'], test_product_id)

    def test_query_inventory_list_by_restock(self):
        """ Query Inventories if quatity is lower than restock_level """
        inventories = []
        for _ in range(5):
            test = Inventory(product_id=_, quantity=_, restock_level=3)
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
            test = Inventory(product_id=_, quantity=_, restock_level=20)
            test.save()
            inventories.append(test)
        for _ in range(2, 5):
            test = Inventory(product_id=_, quantity=_, restock_level=50)
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
        for _ in range(0, 2):
            test = Inventory(product_id=_, quantity=_,
                             restock_level=20, condition='new')
            test.save()
            inventories.append(test)
        for _ in range(0, 2):
            test = Inventory(product_id=_, quantity=_,
                             restock_level=20, condition='used')
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
        resp = self.app.get('/inventory',
                            query_string='condition={}'.format(test_condition))
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
        for _ in range(0, 2):
            test = Inventory(product_id=_, quantity=30, restock_level=20,
                             condition='new', available=True)
            test.save()
            inventories.append(test)
        for _ in range(2, 5):
            test = Inventory(product_id=_, quantity=30, restock_level=50,
                             condition='new', available=False)
            test.save()
            inventories.append(test)
        resp = self.app.get('/inventory',
                            query_string='available=true')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)
        for inventory in data:
            self.assertEqual(inventory['available'], True)
        resp = self.app.get('/inventory',
                            query_string='available=false')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 3)
        for inventory in data:
            self.assertEqual(inventory['available'], False)

    def test_update_inventory(self):
        """ Update an existing Inventory """
        test_inventory = {"inventory_id": 1,
                          "product_id": 2,
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
        self.assertEqual(inventory['inventory_id'], 1)
        inventory['condition'] = 'used'
        resp = self.app.put('/inventory/{}'.format(inventory['inventory_id']),
                            json=inventory,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # get the inventory again
        resp = self.app.get(
            '/inventory/{}'.format(inventory['inventory_id']),
            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_inventory = resp.get_json()
        self.assertEqual(updated_inventory['condition'], 'used')
        # test updating an inventory with wrong inventory_id
        wrong_inventory_id = 2
        resp = self.app.put('/inventory/{}'.format(wrong_inventory_id),
                            json=inventory,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_inventory(self):
        """ Delete an inventory """
        inventory = self._create_inventories(1)[0]
        resp = self.app.delete('/inventory/{}'.format(inventory.inventory_id),
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get('/inventory/{}'.format(inventory.inventory_id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    #####  Mock data #####
    @patch('service.models.Inventory.find_by_condition')
    def test_bad_request(self, bad_request_mock):
        """ Test a bad request error from find_by_condition """
        bad_request_mock.side_effect = DataValidationError()
        resp = self.app.get('/inventory', query_string='condition=wrong')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('service.models.Inventory.find_by_condition')
    def test_internal_server_error(self, request_mock):
        """ Test a request with internal_server_error """
        request_mock.side_effect = internal_server_error("")
        resp = self.app.get('/inventory', query_string='condition=wrong')
        self.assertEqual(resp.status_code, \
                         status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_invalid_method_request(self):
        """ Test an invalid request error """
        resp = self.app.delete('/inventory', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_bad_content_type(self):
        """ Bad content type return 415 """
        test_inventory = InventoryFactory()
        resp = self.app.post('/inventory',
                             json=test_inventory.serialize(),
                             content_type='text/html')
        self.assertEqual(resp.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
