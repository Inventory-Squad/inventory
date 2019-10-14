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
from flask_api import status    # HTTP Status Codes
from service.models import Inventory, DB
from service.service import app, init_db, initialize_logging

DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://root:passw0rd@localhost:3306/mysql')

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

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
