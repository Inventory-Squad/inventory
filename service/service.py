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
PUT /inventory/{product-id}/disable to disable the product #25
DELETE /inventory/reset

"""

import sys
import logging
from flask import jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from flask_restplus import Api, Resource, fields, reqparse, inputs
from service.models import Inventory, DataValidationError

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    return app.send_static_file('index.html')

######################################################################
# GET HEALTH CHECK
######################################################################
@app.route('/healthcheck')
def healthcheck():
    """ Let them know our heart is still beating """
    return make_response(jsonify(status=200, message='Healthy'),
                         status.HTTP_200_OK)

api = Api(app,
          version='1.0.0',
          title='Inventory REST API Service',
          description='This is a Inventory server.',
          default='inventory',
          default_label='Inventory operations',
          doc='/apidocs/index.html',
         )

app.config['RESTPLUS_MASK_SWAGGER'] = False

inventory_model = api.model('Inventory', {
    '_id': fields.String(readOnly=True,
                         description='The unique id assigned \
                         internally by service'),
    'product_id': fields.Integer(required=True,
                                 description='The product id \
                                 of the Inventory'),
    'quantity': fields.Integer(required=True,
                               description='The quantity of \
                               the Inventory'),
    'restock_level': fields.Integer(required=True,
                                    description='The restock \
                                    level of the Inventory'),
    'condition': fields.String(required=True,
                               description='The condition of \
                               the Inventory (e.g., new, open_box, used)'),
    'available': fields.Boolean(required=True,
                                description='The availability \
                                of the Inventory.')
})

create_model = api.model('Inventory', {
    'product_id': fields.Integer(required=True,
                                 description='The product id \
                                 of the Inventory'),
    'quantity': fields.Integer(required=True,
                               description='The quantity of \
                               the Inventory'),
    'restock_level': fields.Integer(required=True,
                                    description='The restock \
                                    level of the Inventory'),
    'condition': fields.String(required=True,
                               description='The condition of \
                               the Inventory (e.g., new, open_box, used)'),
    'available': fields.Boolean(required=True,
                                description='The availability \
                                of the Inventory.')
})

# query string arguments
inventory_args = reqparse.RequestParser()
inventory_args.add_argument('product-id', type=int,
                            required=False, location='args', \
                            help='List Inventory by product id')
inventory_args.add_argument('condition', type=str,
                            required=False, location='args', \
                            help='List Inventory by condition')
inventory_args.add_argument('available', type=inputs.boolean,
                            required=False, location='args', \
                            help='List Inventory by availability')
inventory_args.add_argument('restock-level', type=int,
                            required=False, location='args', \
                            help='List Inventory by restock level')
inventory_args.add_argument('restock', type=inputs.boolean,
                            required=False, location='args', \
                            help='List Inventory by need restock or not')

######################################################################
# Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message
    }, status.HTTP_400_BAD_REQUEST

######################################################################
#  PATH: /inventory/{id}
######################################################################
@api.route('/inventory/<inventory_id>')
@api.param('inventory_id', 'The Inventory identifier')
class InventoryResource(Resource):
    """
    InventoryResource class
    Allows the manipulation of a single Inventory
    GET /inventory/{id} - Returns an Inventory with the id
    PUT /inventory/{id} - Update an Inventory with the id
    DELETE /inventory/{id} -  Deletes an Inventory with the id
    """
    #------------------------------------------------------------------
    # RETRIEVE A INVENTORY
    #------------------------------------------------------------------
    @api.doc('get_inventory')
    @api.response(404, 'Inventory not found')
    @api.marshal_with(inventory_model)
    def get(self, inventory_id):
        """
        Retrieve a single Inventory
        This endpoint will return an Inventory based on it's id
        """
        app.logger.info('Request for inventory with id: %s', inventory_id)
        inventory = Inventory.find(inventory_id)
        if not inventory:
            api.abort(status.HTTP_404_NOT_FOUND,
                      "Inventory with id '{}' was not \
                      found.".format(inventory_id))
        return inventory.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE AN INVENTORY
    #------------------------------------------------------------------
    @api.doc('delete_inventory')
    @api.response(204, 'Inventory deleted')
    def delete(self, inventory_id):
        """
        Delete an inventory
        This endpoint will delete an inventory based on the id specified
        in the path
        """
        app.logger.info('Request to delete inventory with id: %s',
                        inventory_id)
        inventory = Inventory.find(inventory_id)
        if inventory:
            inventory.delete()
        return '', status.HTTP_204_NO_CONTENT

    #------------------------------------------------------------------
    # UPDATE AN EXISTING INVENTORY
    #------------------------------------------------------------------
    @api.doc('update_inventory')
    @api.response(404, 'Inventory not found')
    @api.response(400, 'The posted Inventory data was not valid')
    @api.expect(inventory_model)
    @api.marshal_with(inventory_model)
    def put(self, inventory_id):
        """
        Update an Inventory
        This endpoint will update an Inventory based the body that is posted
        """
        app.logger.info('Request to update inventory with id: %s',
                        inventory_id)
        check_content_type('application/json')
        inventory = Inventory.find(inventory_id)
        if not inventory:
            api.abort(status.HTTP_404_NOT_FOUND,
                      "Inventory with id '{}' was not \
                      found.".format(inventory_id))
        inventory.deserialize(request.get_json())
        inventory.id = inventory_id
        inventory.save()
        return inventory.serialize(), status.HTTP_200_OK

######################################################################
# PATH: /inventory
######################################################################
@api.route('/inventory', strict_slashes=False)
class InventoryCollection(Resource):
    """ Handles all interactions with collections of Inventory """
    #------------------------------------------------------------------
    # ADD A NEW Inventory
    #------------------------------------------------------------------
    @api.doc('create_inventory')
    @api.expect(create_model)
    @api.response(400, 'The posted data was not valid')
    @api.response(201, 'Inventory created successfully')
    @api.marshal_with(inventory_model, code=201)
    def post(self):
        """
        Creates an Inventory
        This endpoint will create an Inventory based
        the data in the body that is posted
        """
        app.logger.info('Request to create an inventory')
        check_content_type('application/json')
        inventory = Inventory()
        app.logger.debug('Payload = %s', api.payload)
        inventory.deserialize(api.payload)
        inventory.save()
        location_url = api.url_for(InventoryResource,
                                   inventory_id=inventory.id, _external=True)
        return inventory.serialize(), status.HTTP_201_CREATED, \
        {'Location': location_url}

    #------------------------------------------------------------------
    # LIST ALL Inventory
    #------------------------------------------------------------------
    # GET request to /inventory?product-id={product-id}
    # GET request to /inventory?available={isAvailable}
    # GET request to /inventory?available={isAvailable}&product-id={product-id}
    # GET request to /inventory?restock=true
    # GET request to /inventory?restock-level={restock-level-value}
    # GET request to /inventory?condition={condition}
    # GET request to /inventory?condition={condition}&product-id={product-id}
    @api.doc('list_inventory')
    @api.expect(inventory_args, validate=True)
    @api.marshal_list_with(inventory_model)
    def get(self):
        """ Returns all of the inventory """
        app.logger.info('Request for inventory list')
        inventories = []
        args = inventory_args.parse_args()
        restock = args['restock']
        restock_level = args['restock-level']
        condition = args['condition']
        product_id = args['product-id']
        available = args['available']
        args_len = len(request.args)

        message_invalid_fields = \
        'Only accept query by product-id, available, ' \
        + 'product-id & availabe, condition, product-id & condition, ' \
        + 'restock-level, restock (list all the inventory that need ' \
        + 'to be restocked).'
        message_condition_empty = '{} can\'t be empty'.format('condition')
        message_condition_invalid = '{} must be new, open_box, used'\
        .format('condition')

        if args_len is 0:
            inventories = Inventory.all()
        elif args_len is 1:
            if product_id is not None:
                inventories = Inventory.find_by_product_id(int(product_id))
            elif restock is not None:
                inventories = Inventory.find_by_restock(restock)
            elif restock_level is not None:
                inventories = Inventory.find_by_restock_level\
                (int(restock_level))
            elif condition is not None:
                if condition is '':
                     api.abort(400, message_condition_empty)
                elif condition not in ('new', 'open_box', 'used'):
                    api.abort(400, message_condition_invalid)
                else:
                    inventories = Inventory.find_by_condition(condition)
            elif available is not None:
                inventories = Inventory.find_by_availability(available)
            else:
                api.abort(400, message_invalid_fields)
        elif args_len is 2:
            if condition is not None and product_id is not None:
                if condition is '':
                    api.abort(400, message_condition_empty)
                elif condition not in ('new', 'open_box', 'used'):
                    api.abort(400, message_condition_invalid)
                else:
                    inventories = Inventory.find_by_condition_with_pid(
                        condition, int(product_id))
            elif available is not None and product_id is not None:
                inventories = Inventory.\
                find_by_availability_with_pid(available, int(product_id))
            else:
                api.abort(400, message_invalid_fields)
        else:
            api.abort(400, message_invalid_fields)
        results = [e.serialize() for e in inventories]
        return results, status.HTTP_200_OK

######################################################################
# PATH: /inventory/{product-id}/disable
######################################################################
@api.route('/inventory/<product_id>/disable')
@api.param('product_id', 'The Product identifier')
class DisableResource(Resource):
    """ Disable actions on an Inventory that has a specific product id"""
    @api.doc('disable_inventory')
    def put(self, product_id):
        """
        Disable an Inventory
        This endpoint will update the availability of an Inventory to FALSE
        based on the id specified in the path
        """
        app.logger.info('Request to disable inventory with product id: %s',
                        product_id)
        inventory = Inventory.find_by_product_id(int(product_id))
        for elem in inventory:
            elem.available = False
            elem.save()
        return [elem.serialize() for elem in inventory], status.HTTP_200_OK

######################################################################
# DELETE ALL EXISTING INVENTORY (For testing only)
######################################################################
@app.route('/inventory/reset', methods=['DELETE'])
def reset_inventory():
    """
    Delete all Inventory
    This endpoint will delete all Inventory
    """
    app.logger.info('Delete all inventory')
    Inventory.remove_all()
    return make_response('', status.HTTP_204_NO_CONTENT)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
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
