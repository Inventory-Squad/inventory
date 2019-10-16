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
inventory_id (int) readonly
product_id (int)
quantity (int)
restock_level (int) (when to order more )
condition (string) ( new / open box / used )
available (boolean)
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import and_

# Create the SQLAlchemy object to be initialized later in init_db()
DB = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

class Inventory(DB.Model):
    """
    Class that represents an inventory
    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    logger = logging.getLogger('flask.app')
    app = None

    # Table Schema
    inventory_id = DB.Column(DB.Integer, primary_key=True)
    product_id = DB.Column(DB.Integer)
    quantity = DB.Column(DB.Integer)
    restock_level = DB.Column(DB.Integer)
    condition = DB.Column(DB.String(10))
    available = DB.Column(DB.Boolean())

    def save(self):
        """
        Saves an Inventory to DB
        """
        Inventory.logger.info('Saving an inventory')
        if not self.inventory_id:
            DB.session.add(self)
        else:
            Inventory.logger.info('Inventory with inventory_id: %s is exist', self.inventory_id)
        DB.session.commit()
        Inventory.logger.info('Inventory with inventory_id: %s saved', self.inventory_id)

    def serialize(self):
        """ Serializes an Inventory into a dictionary """
        return {"inventory_id": self.inventory_id,
                "product_id": self.product_id,
                "quantity": self.quantity,
                "restock_level": self.restock_level,
                "condition": self.condition,
                "available": self.available}

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
        return self

    def delete(self):
        """ Removes an Inventory from the data store """
        DB.session.delete(self)
        DB.session.commit()

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        DB.init_app(app)
        app.app_context().push()
        DB.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Inventorys in the database """
        cls.logger.info('Processing all Inventorys')
        return cls.query.all()

    @classmethod
    def find(cls, inventory_id):
        """ Find an Inventory by inventory_id """
        cls.logger.info('Processing lookup for inventory_id %s ...',
                        inventory_id)
        return cls.query.get(inventory_id)

    @classmethod
    def find_or_404(cls, inventory_id):
        """ Find an Inventory by inventory_id """
        cls.logger.info('Processing lookup or 404 for inventory_id %s ...',
                        inventory_id)
        return cls.query.get_or_404(inventory_id)

    @classmethod
    def find_by_product_id(cls, product_id):
        """ Find an Inventory by product_id
            Args:
            product_id (int): the product_id of the Inventory you
            want to match
        """
        return cls.query.filter(cls.product_id == product_id)

    @classmethod
    def find_by_availability(cls, available):
        """ Find an Inventory by availability
        Args:
            available (boolean): the availability of the Inventory you
            want to match
        """
        return cls.query.filter(cls.available == available)

    @classmethod
    def find_by_condition(cls, condition):
        """ Find an Inventory by condition
        Args:
            condition (string): the condition of the Inventory you
            want to match
        """
        return cls.query.filter(cls.condition == condition)

    @classmethod
    def find_by_condition_with_pid(cls, condition, pid):
        """ Find an Inventory by condition and product_id
        Args:
            condition (string): the condition of the Inventory you
            want to match
            product_id (int): the product_id of the Inventory you
            want to match
        """
        return cls.query.filter(
            and_(cls.condition == condition, cls.product_id == pid))

    @classmethod
    def find_by_restock(cls, restock):
        """ Returns all of the Inventory that quantity lower than their\
            restock level
        Args:
            restock (boolean): if restock is true than return the list,\
            if false than return normal list all
        """
        cls.logger.info('Processing quantity < restock_level query ...')
        if restock is True:
            return cls.query.filter(cls.quantity < cls.restock_level)
        return cls.query.filter(cls.quantity >= cls.restock_level)

    @classmethod
    def find_by_restock_level(cls, restock_level):
        """ Returns all of the Inventory that restock level = {restock_level}
        Args:
            restock_level (Integer): the restock level of the inventory \
            you want to match
        """
        cls.logger.info('Processing restock-level query ...')
        return cls.query.filter(cls.restock_level == restock_level)
