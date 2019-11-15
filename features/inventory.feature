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
