Feature: The Inventory service back-end
    As a warehouse Owner
    I need a RESTful catalog service
    So that I can keep track of all inventory

Background:
    Given the following products
        | product_id | quantity | restock_level | condition | available |
        | 1          | 10       | 5             | new       | True      |
        | 1          | 20       | 5             | open_box  | False     |
        | 1          | 10       | 15            | used      | True      |
        | 2          | 20       | 5             | new       | False     |
        | 2          | 10       | 5             | open_box  | True      |
        | 2          | 20       | 15            | used      | False     |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create an inventory
    When I visit the "Home Page"
    And I set the "Product Id" to "5"
    And I set the "Quantity" to "50"
    And I set the "Restock Level" to "20"
    And I select "New" in the "Condition" dropdown
    And I select "True" in the "Available" dropdown
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Inventory ID" field
    And I press the "Clear" button
    Then the "Inventory ID" field should be empty
    And the "Product Id" field should be empty
    And the "Quantity" field should be empty
    And the "Restock Level" field should be empty
    When I paste the "Inventory ID" field
    And I press the "Retrieve" button
    Then I should see "5" in the "Product Id" field
    And I should see "50" in the "Quantity" field
    And I should see "20" in the "Restock Level" field
    And I should see "New" in the "Condition" dropdown
    And I should see "True" in the "Available" dropdown

Scenario: List all inventory
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "6" entries
    And I should see "3" entries for product "1"
    And I should see "3" entries for product "2"
    And I should see "1 10 5 new true" in the results
    And I should see "1 20 5 open_box false" in the results
    And I should see "1 10 15 used true" in the results
    And I should see "2 20 5 new false" in the results
    And I should see "2 10 5 open_box true" in the results
    And I should see "2 20 15 used false" in the results
    And I should see the message "Success"

Scenario: List all inventory by product id
    When I visit the "Home Page"
    And I set the "Product Id" to "1"
    And I press the "Search" button
    Then I should see "3" entries
    And I should see "1 10 5 new" in the results
    And I should see "1 20 5 open_box" in the results
    And I should see "1 10 15 used" in the results
    And I should see the message "Success"

Scenario: List all inventory by condition
    When I visit the "Home Page"
    And I select "New" in the "Condition" dropdown
    And I press the "Search" button
    Then I should see "1 10 5 new" in the results
    And I should see "2 20 5 new" in the results
    And I should see the message "Success"

Scenario: List all inventory by condition and product id
    When I visit the "Home Page"
    And I set the "Product Id" to "1"
    And I select "New" in the "Condition" dropdown
    And I press the "Search" button
    Then I should see "1 10 5 new true" in the results
    And I should see the message "Success"

Scenario: List all inventory by restock level
    When I visit the "Home Page"
    And I set the "Restock Level" to "15"
    And I press the "Search" button
    Then I should see "2" entries
    And I should see "1 10 15 used" in the results
    And I should see "2 20 15 used" in the results
    And I should see the message "Success"

Scenario: List all inventory by availability
    When I visit the "Home Page"
    And I select "True" in the "Available" dropdown
    And I press the "Search" button
    Then I should see "1 10 5 new" in the results
    Then I should see "1 10 15 used" in the results
    And I should see "2 10 5 open_box" in the results
    And I should see the message "Success"

Scenario: List all inventory by restock need
    When I visit the "Home Page"
    And I press the "restock-list" button
    Then I should see "1" entries
    And I should see "1 10 15 used" in the results
    And I should see the message "Success"

Scenario: Retrieve an inventory by inventory id
    When I visit the "Home Page"
    And I set the "Product Id" to "1"
    And I select "New" in the "Condition" dropdown
    And I press the "Search" button
    When I copy the first ID field from the search results
    And I paste the "Inventory ID" field
    And I press the "Retrieve" button
    Then I should see "1" in the "Product Id" field
    And I should see "10" in the "Quantity" field
    And I should see "5" in the "Restock Level" field
    And I should see "New" in the "Condition" dropdown
    And I should see "True" in the "Available" dropdown

Scenario: Delete an inventory
    When I visit the "Home Page"
    And I set the "Product Id" to "1"
    And I select "New" in the "Condition" dropdown
    And I press the "Search" button
    When I copy the first ID field from the search results
    And I paste the "Inventory ID" field
    And I press the "Delete" button
    Then I should see the message "has been Deleted!"
    When I paste the "Inventory ID" field
    And I press the "Retrieve" button
    Then I should see the message "Invalid Inventory"

Scenario: Update an inventory
    When I visit the "Home Page"
    And I set the "Product Id" to "2"
    And I select "New" in the "Condition" dropdown
    And I press the "Search" button
    Then I should see "2 20 5 new" in the results
    When I copy the first ID field from the search results
    And I paste the "Inventory ID" field
    And I press the "Retrieve" button
    Then I should see "New" in the "Condition" dropdown
    When I change "Condition" dropdown to "Open Box"
    And I press the "Update" button
    Then I should see the message "has been Updated!"
    And I should see "Open Box" in the "Condition" dropdown
    And I should see "2 20 5 open_box" in the results
    And I should not see "2 20 5 new " in the results

Scenario: Disable an inventory
    When I visit the "Home Page"
    And I set the "Product Id" to "2"
    And I press the "Disable" button
    Then I should see the message "Product 2 has been Disabled!"
    Then I should not see "True" in the results
