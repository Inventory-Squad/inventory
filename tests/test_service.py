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
from flask_api import status    # HTTP Status Codes
from service.models import DB, Inventory
from service.service import app, init_db, initialize_logging

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
            test = Inventory(product_id=1, quantity=100, restock_level=50,
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

    def test_get_inventory_list(self):
        """ Get a list of Inventory """
        self._create_inventories(5)
        resp = self.app.get('/inventory')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

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

    def test_update_inventory(self):
        """ Update an existing Inventory """
        test_inventory = {"inventory_id": 1,
                          "product_id": 2,
                          "quantity": 100,
                          "restock_level": 40,
                          "condition": 'new',
                          "available": True}
        resp = self.app.post('/inventory',
                             json=json.dumps(test_inventory),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        inventory = resp.get_json()
        self.assertEqual(inventory['condition'], 'new')
        self.assertEqual(inventory['inventory_id'], 1)
        # self._create_inventories(100)
        # resp = self.app.get('/inventory')
        # self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # data = resp.get_json()
        # for i in data:
        #     if i['condition'] == 'new':
        #         inventory = i
        #         break
        # update the inventory
        inventory['condition'] = 'used'
        resp = self.app.put('/inventory/{}'.format(inventory['inventory_id']),
                            json=inventory,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # get the inventory again
        resp = self.app.get(
            '/inventory/{}'.format(inventory['inventory_id']), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_inventory = resp.get_json()
        self.assertEqual(updated_inventory['condition'], 'used')
        # test updating an inventory with wrong inventory_id
        wrong_inventory_id = 2
        resp = self.app.put('/inventory/{}'.format(wrong_inventory_id),
                            json=inventory,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        # test updating an inventory with bad data
        inventory['product_id'] = 3
        inventory['wrong_attr'] = 'wrong'
        resp = self.app.put('/inventory/{}'.format(inventory['inventory_id']),
                            json=inventory,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
