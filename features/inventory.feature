Feature: The Inventory service back-end
    As a warehouse Owner
    I need a RESTful catalog service
    So that I can keep track of all inventory

Background:
    Given the following products 
        | product_id | quantity | restock_level | condition | available |
        | 1          | 10       | 5             | new       | True      |
        | 1          | 20       | 5             | open box  | False     |
        | 1          | 10       | 15            | used      | True      |
        | 2          | 20       | 5             | new       | False     |
        | 2          | 10       | 5             | open box  | True      |
        | 2          | 20       | 15            | used      | False     |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory REST API Service" in the title
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
    And I should see "New" in the "Condition" dropdow
    And I should see "True" in the "Available" dropdow

Scenario: List all inventory    

Scenario: List all inventory by product id

Scenario: List all inventory by condition

Scenario: List all inventory by condition and product id

Scenario: List all inventory by restock level

Scenario: List all inventory by availability

Scenario: List all inventory by restock need

Scenario: Delete an inventory

Scenario: Update an inventory

Scenario: Disable an inventory
