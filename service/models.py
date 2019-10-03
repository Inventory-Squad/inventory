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
The inventory resource keeps track of how many of each product we have in our warehouse

Attributes:
-----------
inventory_id (int) readonly
product_id (string) readonly
quantity (int)
restock_level (int) (when to order more )
condition (string) ( new / open box / used )
available (boolean)

"""
import logging
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Inventory(db.Model):
    """
    Class that represents an inventory

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    logger = logging.getLogger('flask.app')
    app = None

    # Table Schema
    inventory_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(63))
    quantity = db.Column(db.Integer)
    restock_level = db.Column(db.Integer)
    condition = db.Column(db.String(10))
    available = db.Column(db.Boolean())

    def __repr__(self):
        return '<Inventory %r>' % (self.inventory_id)

    def save(self):
        """
        Saves an Inventory to the data store
        """
        Inventory.logger.info('Saving %s', self.inventory_id)
        if not self.inventory_id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Removes an Inventory from the data store """
        Inventory.logger.info('Deleting %s', self.inventory_id)
        db.session.delete(self)
        db.session.commit()

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
        except TypeError as error:
            raise DataValidationError('Invalid Inventory: body of request contained' \
                                      'bad or no data')
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Inventorys in the database """
        cls.logger.info('Processing all Inventorys')
        return cls.query.all()

    @classmethod
    def find(cls, inventory_id):
        """ Finds a Inventory by it's ID """
        cls.logger.info('Processing lookup for id %s ...', inventory_id)
        return cls.query.get(inventory_id)

    @classmethod
    def find_or_404(cls, inventory_id):
        """ Find a Inventory by it's id """
        cls.logger.info('Processing lookup or 404 for id %s ...', inventory_id)
        return cls.query.get_or_404(inventory_id)

    @classmethod
    def find_by_product_id(cls, product_id):
        """ Returns all Inventorys with the given product_id

        Args:
            product_id (string): the product_id of the Inventorys you want to match
        """
        cls.logger.info('Processing product_id query for %s ...', product_id)
        return cls.query.filter(cls.product_id == product_id)

    @classmethod
    def find_by_condition(cls, condition):
        """ Returns all of the Inventorys in a condition

        Args:
            condition (string): the condition of the Inventorys you want to match
        """
        cls.logger.info('Processing condition query for %s ...', condition)
        return cls.query.filter(cls.condition == condition)

    @classmethod
    def find_by_availability(cls, available=True):
        """ Query that finds Inventorys by their availability """
        """ Returns all Inventorys by their availability

        Args:
            available (boolean): True for Inventorys that are available
        """
        cls.logger.info('Processing available query for %s ...', available)
        return cls.query.filter(cls.available == available)

    @classmethod
    def find_by_restock(cls, restock_level):
        """ Query that finds Inventorys by their restock_level """
        """ Returns all Inventorys by their restock_level

        Args:
            restock_level (int)
        """
        cls.logger.info('Processing restock_level query for %s ...', restock_level)
        return cls.query.filter(cls.restock_level == restock_level)

    @classmethod
    def find_quantity_lower_restock(cls):
        """ Query that finds Inventorys that qunatity lower than their restock level """
        """ Returns all Inventorys if their qunatity lower than their restock level
        """
        cls.logger.info('Processing find_quantity_lower_restock query ...')
        return cls.query.filter(cls.quantity < cls.restock_level)
