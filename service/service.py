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
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.

"""

Paths (#issue_number):
------

GET /inventory #3
GET /inventory/{inventory-id} #31
GET /inventory?product-id={pid} #4
GET /inventory?condition={condition} #5
GET /inventory?restock=true #2
GET /inventory?restock-level={restock-level-value} #2
POST /inventory #6
PUT /inventory/{inventory-id} #7
DELETE /inventory/{inventory-id} #8
PUT /inventory/product_id/{product_id} // to disable the product #25

"""

import sys
import logging
from flask import jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound
from service.models import Inventory, DataValidationError

# Import Flask application
from . import app

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_400_BAD_REQUEST,
                   error='Bad Request',
                   message=message), status.HTTP_400_BAD_REQUEST

@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_404_NOT_FOUND,
                   error='Not Found',
                   message=message), status.HTTP_404_NOT_FOUND

@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                   error='Method not Allowed',
                   message=message), status.HTTP_405_METHOD_NOT_ALLOWED

@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                   error='Unsupported media type',
                   message=message), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = str(error)
    app.logger.error(message)
    return jsonify(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                   error='Internal Server Error',
                   message=message), status.HTTP_500_INTERNAL_SERVER_ERROR


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    return jsonify(name='Inventory REST API Service',
                   version='1.0',
                   paths=url_for('list_inventory', _external=True)
                  ), status.HTTP_200_OK

######################################################################
# ADD an Inventory
######################################################################
@app.route('/inventory', methods=['POST'])
def create_inventory():
    """
    Creates an Inventory
    This endpoint will create an Inventory based the data in the body
    that is posted
    """
    app.logger.info('Request to create an inventory')
    check_content_type('application/json')
    inventory = Inventory()
    inventory.deserialize(request.get_json())
    inventory.save()
    message = inventory.serialize()
    # location_url = url_for('get_inventory',
    # inventory_id=inventory.inventory_id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': 'location_url'
                         })
######################################################################
# RETRIEVE An Inventory
######################################################################
@app.route('/inventory/<int:inventory_id>', methods=['GET'])
def get_inventory(inventory_id):
    """
    Retrieve a single Inventory
    This endpoint will return an Inventory based on it's id
    """
    app.logger.info('Request for inventory with id: %s', inventory_id)
    inventory = Inventory.find(inventory_id)
    if not inventory:
        raise NotFound("Inventory with inventory_id '{}' was not found."
                       .format(inventory_id))
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

######################################################################
# LIST ALL Inventory
######################################################################
# GET request to /inventory?product-id={product-id}
# GET request to /inventory?available={isAvailable}
# GET request to /inventory?restock=true
# GET request to /inventory?restock-level={restock-level-value}

@app.route('/inventory', methods=['GET'])
def list_inventory():
    """ Returns all of the inventory """
    app.logger.info('Request for inventory list')
    inventories = []
    restock = request.args.get('restock')
    restock_level = request.args.get('restock-level')
    product_id = request.args.get('product-id')
    available = request.args.get('available')
    if restock:
        if restock == "true":
            inventories = Inventory.find_by_restock(True)
        elif restock == "false":
            inventories = Inventory.find_by_restock(False)
    elif restock_level:
        inventories = Inventory.find_by_restock_level(restock_level)
    elif product_id:
        inventories = Inventory.find_by_product_id(product_id)
    elif available:
        if available == 'true':
            inventories = Inventory.find_by_availability(True)
        elif available == 'false':
            inventories = Inventory.find_by_availability(False)
    else:
        inventories = Inventory.all()
    results = [e.serialize() for e in inventories]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# DISABLE AN EXISTING INVENTORY
######################################################################
@app.route('/inventory/disable/<int:product_id>', methods=['PUT'])
def disable_inventory(product_id):
    """
    Disable an Inventory
    This endpoint will update the availability of an Inventory to FALSE
    based on the id specified in the path
    """
    app.logger.info('Request to disable inventory with id: %s', product_id)
    check_content_type('application/json')

    inventory = Inventory.find_by_product_id(product_id)

    if not inventory:
        raise NotFound("Inventory with id '{}' was not found."
                       .format(product_id))
    for elem in inventory:
        elem.available = False
        elem.save()
    return make_response(jsonify([elem.serialize() for elem in inventory]),
                         status.HTTP_200_OK)

######################################################################
# DELETE AN INVENTORY
######################################################################
@app.route('/inventory/<int:inventory_id>', methods=['DELETE'])
def delete_inventory(inventory_id):
    """
    Delete an inventory
    This endpoint will delete an inventory based on the id specified
    in the path
    """
    app.logger.info('Request to delete inventory with id: %s', inventory_id)
    inventory = Inventory.find(inventory_id)
    if inventory:
        inventory.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# UPDATE AN EXISTING INVENTORY
######################################################################
@app.route('/inventory/<int:inventory_id>', methods=['PUT'])
def update_inventory(inventory_id):
    """
    Update an Inventory
    This endpoint will update an Inventory based the body that is posted
    """
    app.logger.info('Request to update inventory with id: %s', inventory_id)
    check_content_type('application/json')
    inventory = Inventory.find(inventory_id)
    if not inventory:
        raise NotFound(
            "Inventory with id '{}' was not found.".format(inventory_id))
    inventory.deserialize(request.get_json())
    inventory.id = inventory_id
    inventory.save()
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Inventory.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s',
                     request.headers['Content-Type'])
    abort(415, 'Content-Type must be {}'.format(content_type))

def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print('Setting up logging...')
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.propagate = False
        app.logger.info('Logging handler established')
