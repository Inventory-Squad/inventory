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


@given(u'the following products')
def step_impl(context):
    """ Delete all Inventory entries and load new ones """
    create_url = context.base_url + '/inventory'
    headers = {'Content-Type': 'application/json'}
    context.resp = requests.delete(
        create_url + '/reset', headers=headers)
    expect(context.resp.status_code).to_equal(204)
    for row in context.table:
        data = {
            "product_id": int(row['product_id']),
            "quantity": int(row['quantity']),
            "restock_level": int(row['restock_level']),
            "condition": row["condition"],
            "available": bool(row['available']),
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)


@when(u'I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)

@then(u'I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)

@then(u'I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)

@when(u'I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_name = element_name.replace(" ", "_")
    element_id = element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)

@when(u'I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_name = element_name.replace(" ", "_")
    element_id = element_name.lower()
    element = Select(context.driver.find_element_by_id(element_id))
    text = text.replace(" ", "_")
    element.select_by_visible_text(text)

@then(u'I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_name = element_name.replace(" ", "_")
    element_id = element_name.lower()
    element = Select(context.driver.find_element_by_id(element_id))
    expect(element.first_selected_option.text).to_equal(text)

@then(u'I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_name = element_name.replace(" ", "_")
    element_id = element_name.lower()
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    expect(found).to_be(True)

@then(u'the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_name = element_name.replace(" ", "_")
    element_id = element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    expect(element.get_attribute('value')).to_be(u'')

@then('I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search_results')
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)
    
##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_name = element_name.replace(" ", "_")
    element_id = element_name.lower()
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_name = element_name.replace(" ", "_")
    element_id = element_name.lower()
    element = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clean button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################

@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()

@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'flash_message'),
            message
        )
    )
    expect(found).to_be(True)

@then(u'I should see "{num}" entries')
def step_impl(context, num):
    element = context.driver.find_element_by_id("search_results")
    rows = element.find_elements_by_xpath("//table/tbody[2]/tr")
    error_msg = f"Unexpected number of rows - {len(rows)}"
    ensure(len(rows), int(num), error_msg)

@then(u'I should see "{num}" entries for product "{product_id}"')
def step_impl(context, num, product_id):
    element = context.driver.find_element_by_id("search_results")
    rows = element.find_elements_by_xpath("//table/tbody[2]/tr/td[2]")
    matching = [row for row in rows if (int(row.text) == int(product_id))]
    error_msg = f"Unexpected number of rows for {product_id} - {len(matching)}"
    ensure(len(matching), int(num), error_msg)
