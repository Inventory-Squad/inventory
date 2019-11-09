# Copyright 2016, 2019 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Models for Inventory Service
All of the models are stored in this module
Models
------
The inventory resource keeps track of how many
of each product we have in our warehouse
Attributes:
-----------
id (int) readonly
product_id (int)
quantity (int)
restock_level (int) (when to order more )
condition (string) ( new / open box / used )
available (boolean)
"""
import os
import json
import logging
from cloudant.client import Cloudant
from cloudant.query import Query
from requests import HTTPError

# get configruation from enviuronment (12-factor)
ADMIN_PARTY = os.environ.get('ADMIN_PARTY', 'False').lower() == 'true'
CLOUDANT_HOST = os.environ.get('CLOUDANT_HOST', 'localhost')
CLOUDANT_USERNAME = os.environ.get('CLOUDANT_USERNAME', 'admin')
CLOUDANT_PASSWORD = os.environ.get('CLOUDANT_PASSWORD', 'pass')

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

class Inventory():
    """
    Class that represents an inventory
    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    logger = logging.getLogger('flask.app')
    client = None   # cloudant.client.Cloudant
    database = None # cloudant.database.CloudantDatabase

    def __init__(self, product_id=None,
                 quantity=None, restock_level=None,
                 condition=None, available=None):
        self.id = None
        self.product_id = product_id
        self.quantity = quantity
        self.restock_level = restock_level
        self.condition = condition
        self.available = available

    def create(self):
        """
        Creates a new Inventory in the database
        """
        try:
            Inventory.logger.info("Create an new inventory")
            document = self.database.create_document(self.serialize())
        except HTTPError as err:
            Inventory.logger.warning('Create failed: %s', err)
            return

        if document.exists():
            self.id = document['_id']
            print("create" + self.id)

    def update(self):
        """ Updates an Inventory in the database """
        if self.id:
            Inventory.logger.info("Update an inventory: {%s}", self.id)
            try:
                document = self.database[self.id]
            except KeyError:
                document = None
            if document:
                document.update(self.serialize())
                document.save()

    def save(self):
        """
        Saves an Inventory to DB
        """
        if self.id:
            self.update()
        else:
            self.create()

    def serialize(self):
        """ Serializes an Inventory into a dictionary """
        inventory = {
            "product_id": self.product_id,
            "quantity": self.quantity,
            "restock_level": self.restock_level,
            "condition": self.condition,
            "available": self.available
        }
        if self.id:
            inventory['_id'] = self.id
        return inventory

    def deserialize(self, data):
        """
        Deserializes a Inventory from a dictionary
        Args:
            data (dict): A dictionary containing the Inventory data
        """
        try:
            self.product_id = data['product_id']
            self.quantity = data['quantity']
            self.restock_level = data['restock_level']
            self.condition = data['condition']
            self.available = data['available']
            if type(self.product_id) is not int:
                raise TypeError('product_id required int')
            if type(self.quantity) is not int:
                raise TypeError('quantity required int')
            if type(self.restock_level) is not int:
                raise TypeError('restock_level required int')
            if not isinstance(self.condition, str):
                raise TypeError('condition required string')
            if type(self.available) is not bool:
                raise TypeError('available required bool')
        except KeyError as error:
            raise DataValidationError('Invalid Inventory: missing '
                                      + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid Inventory: body of ' \
                                      'request contained ' \
                                      'bad or no data : ' \
                                      + error.args[0])
        # if there is no id and the data has one, assign it
        if not self.id and '_id' in data:
            self.id = data['_id']

        return self

    def delete(self):
        """ Deletes an Inventory from the database """
        if self.id:
            try:
                document = self.database[self.id]
            except KeyError:
                document = None
            if document:
                document.delete()

######################################################################
#  S T A T I C   D A T A B S E   M E T H O D S
######################################################################
    @classmethod
    def connect(cls):
        """ Connect to the server """
        cls.client.connect()

    @classmethod
    def disconnect(cls):
        """ Disconnect from the server """
        cls.client.disconnect()

    @classmethod
    def remove_all(cls):
        """ Removes all documents from the database (use for testing)  """
        for document in cls.database:
            document.delete()

    @classmethod
    def all(cls):
        """ Query that returns all Inventory """
        results = []
        for doc in cls.database:
            inventory = Inventory().deserialize(doc)
            inventory.id = doc['_id']
            results.append(inventory)
        return results

######################################################################
#  F I N D E R   M E T H O D S
######################################################################

    @classmethod
    def find(cls, inventory_id):
        """ Find an Inventory by id """
        cls.logger.info('Processing lookup for id %s ...',
                        inventory_id)
        try:
            document = cls.database[inventory_id]
            print(document)
            return Inventory().deserialize(document)
        except KeyError:
            return None

    @classmethod
    def find_by(cls, **kwargs):
        """ Find records using selector """
        query = Query(cls.database, selector=kwargs)
        results = []
        for doc in query.result:
            inventory = Inventory()
            inventory.deserialize(doc)
            results.append(inventory)
        return results


    @classmethod
    def find_by_product_id(cls, product_id):
        """ Find an Inventory by product_id
            Args:
            product_id (int): the product_id of the Inventory you
            want to match
        """
        # return cls.query.filter(cls.product_id == product_id)
        return cls.find_by(product_id=product_id)

    @classmethod
    def find_by_availability(cls, available):
        """ Find an Inventory by availability
        Args:
            available (boolean): the availability of the Inventory you
            want to match
        """
        # return cls.query.filter(cls.available == available)
        return cls.find_by(available=available)

    @classmethod
    def find_by_condition(cls, condition):
        """ Find an Inventory by condition
        Args:
            condition (string): the condition of the Inventory you
            want to match
        """
        # return cls.query.filter(cls.condition == condition)
        return cls.find_by(condition=condition)

    @classmethod
    def find_by_condition_with_pid(cls, condition, pid):
        """ Find an Inventory by condition and product_id
        Args:
            condition (string): the condition of the Inventory you
            want to match
            product_id (int): the product_id of the Inventory you
            want to match
        """
        # return cls.query.filter(
        #     and_(cls.condition == condition, cls.product_id == pid))
        return cls.find_by(condition=condition, product_id=pid)

    @classmethod
    def find_by_restock(cls, restock):
        """ Returns all of the Inventory that quantity lower than their\
            restock level
        Args:
            restock (boolean): if restock is true than return the list,\
            if false than return normal list all
        """
        cls.logger.info('Processing quantity < restock_level query ...')
        results = []
        for doc in cls.database:
            inventory = Inventory().deserialize(doc)
            if restock is True:
                if inventory.quantity < inventory.restock_level:
                    results.append(inventory)
            else:
                if inventory.quantity >= inventory.restock_level:
                    results.append(inventory)
        return results

    @classmethod
    def find_by_restock_level(cls, restock_level):
        """ Returns all of the Inventory that restock level = {restock_level}
        Args:
            restock_level (Integer): the restock level of the inventory \
            you want to match
        """
        cls.logger.info('Processing restock-level query ...')
        return cls.find_by(restock_level=restock_level)

############################################################
#  C L O U D A N T   D A T A B A S E   C O N N E C T I O N
############################################################
    @staticmethod
    def init_db(dbname='asd'):
        """
        Initialized Coundant database connection
        """
        opts = {}
        # Try and get VCAP from the environment
        if 'VCAP_SERVICES' in os.environ:
            Inventory.logger.info('Found Cloud Foundry VCAP_SERVICES bindings')
            vcap_services = json.loads(os.environ['VCAP_SERVICES'])
            # Look for Cloudant in VCAP_SERVICES
            for service in vcap_services:
                if service.startswith('cloudantNoSQLDB'):
                    opts = vcap_services[service][0]['credentials']

        # if VCAP_SERVICES isn't found, maybe we are running on Kubernetes?
        if not opts and 'BINDING_CLOUDANT' in os.environ:
            Inventory.logger.info('Found Kubernetes BINDING_CLOUDANT bindings')
            opts = json.loads(os.environ['BINDING_CLOUDANT'])

        # If Cloudant not found in VCAP_SERVICES or BINDING_CLOUDANT
        # get it from the CLOUDANT_xxx environment variables
        if not opts:
            Inventory.logger.info('VCAP_SERVICES and \
                                  BINDING_CLOUDANT undefined.')
            opts = {
                "username": CLOUDANT_USERNAME,
                "password": CLOUDANT_PASSWORD,
                "host": CLOUDANT_HOST,
                "port": 5984,
                "url": "http://"+CLOUDANT_HOST+":5984/"
            }

        if any(k not in opts for k in ('host', 'username',
                                       'password', 'port', 'url')):
            raise ConnectionError('Error - Failed \
                                          to retrieve options. ' \
                                          'Check that app is bound to \
                                          a Cloudant service.')

        Inventory.logger.info('Cloudant Endpoint: %s', opts['url'])
        try:
            if ADMIN_PARTY:
                Inventory.logger.info('Running in Admin Party Mode...')
            Inventory.client = Cloudant(
                opts['username'],
                opts['password'],
                url=opts['url'],
                connect=True,
                auto_renew=True,
                admin_party=ADMIN_PARTY
            )
        except ConnectionError:
            raise ConnectionError('Cloudant service \
                                          could not be reached')

        # Create database if it doesn't exist
        try:
            Inventory.database = Inventory.client[dbname]
        except KeyError:
            # Create a database using an initialized client
            Inventory.database = Inventory.client.create_database(dbname)
        # check for success
        if not Inventory.database.exists():
            raise ConnectionError('Database [{}] could not \
                                          be obtained'.format(dbname))
