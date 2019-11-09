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
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""
import os
import sys
from flask import Flask

# Get configuration from environment
SECRET_KEY = os.getenv('SECRET_KEY', 's3cr3t-key-shhhh')

# Create Flask application
app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY

# Import the rutes After the Flask app is created
from service import service, models
from .models import Inventory

# Set up logging for production
service.initialize_logging()

app.logger.info(70 * '*')
app.logger.info('  P R O M O T I O N   S E R V I C E   \
                R U N N I N G  '.center(70, '*'))
app.logger.info(70 * '*')

@app.before_first_request
def init_db(dbname='asd'):
    """ Initlaize the CouchDB """
    Inventory.init_db(dbname)

app.logger.info('Service initialized!')
