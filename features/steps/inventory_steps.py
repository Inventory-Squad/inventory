"""
Inventory Steps

Steps file for Inventory.feature

"""
from os import getenv
import logging
import json
import requests
from behave import *
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions

WAIT_SECONDS = int(getenv('WAIT_SECONDS', '60'))


@given('the following products')
def step_impl(context):
    """ Delete all Inventory entries and load new ones """
    create_url = context.base_url + '/inventory'
    for row in context.table:
        context.resp = requests.delete(
            create_url + '/' + row['product_id'])
        expect(context.resp.status_code).to_equal(200)
    headers = {'Content-Type': 'application/json'}
    for row in context.table:
        data = {
            "product_id": int(row['product_id']),
            "quantity": int(row['quantity']),
            "restock_level": int(row['restock_level']),
            "condition": row["condition"],
            "available": row['available'],
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)


@when('I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    #context.driver.save_screenshot('home_page.png')

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)

@then('I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)

@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_name = element_name.replace(" ", "_")
    element_id = element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)

@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_name = element_name.replace(" ", "_")
    element_id = element_name.lower()
    element = Select(context.driver.find_element_by_id(element_id))
    text = text.replace(" ", "_")
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_name = element_name.replace(" ", "_")
    element_id = element_name.lower()
    element = Select(context.driver.find_element_by_id(element_id))
    expect(element.first_selected_option.text).to_equal(text)


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_name = element_name.replace(" ", "_")
    element_id = element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    expect(element.get_attribute('value')).to_be(u'')
