[![Build Status](https://travis-ci.org/Inventory-Squad/inventory.svg?branch=master)](https://travis-ci.org/Inventory-Squad/inventory)
[![codecov](https://codecov.io/gh/Inventory-Squad/inventory/branch/master/graph/badge.svg)](https://codecov.io/gh/Inventory-Squad/inventory)
# Inventory
The inventory resource keeps track of how many of each product we have in our warehouse.

## Setting up your Development Environment
To get started, download and install VirtualBox and Vagrant.

### Install using Vagrant and VirtualBox
```bash
    git clone git@github.com:Inventory-Squad/inventory.git
    cd inventory
    vagrant up
    vagrant ssh
    cd /vagrant
```

## Manually running the Tests

### BDD
BDD integration tests are using Selenium to manipulate a web page on a running server.

Run the tests using `behave`
```shell
    $ honcho start &
    $ behave
```

Note that the `&` runs the server in the background. To stop the server, you must bring it to the foreground and then press `Ctrl+C`

Stop the server with
```shell
    $ fg
    $ <Ctrl+C>
```

Alternately you can run the server in another `shell` by opening another terminal window and using `vagrant ssh` to establish a second connection to the VM. You can also suppress all log output in the current shell with this command:

```bash
    honcho start 2>&1 > /dev/null &
```

or you can supress info logging with this command:

```bash
    gunicorn --bind 0.0.0.0 --log-level=error service:app &
```

This will suppress the normal `INFO` logging

### TDD
This repo also has unit tests that you can run `nose`

```bash
    $ nosetests
```

Nose is configured to automatically include the flags `--with-spec --spec-color` so that red-green-refactor is meaningful. If you are in a command shell that supports colors, passing tests will be green while failing tests will be red.

When you are done, you can exit and shut down the vm with:

```bash
    exit
    vagrant halt
```

If the VM is no longer needed you can remove it with:

```bash
    vagrant destroy
```



## Attributes

| Fields        | Type                                 |
| :------------ | :----------------------------------- |
| id  | String, read only                   |
| product_id    | Integer                              |
| quantity      | Integer                              |
| restock_level | Integer, when to order more          |
| condition     | String,  {'new', 'open_box', 'used'} |
| available     | Boolean                              |



## API Endpoint

An API to allow management of inventory for an e-commerce website. It will support create, read, update, delete, list, query, and an action(disable an entry).

##### Create a new inventory

- PATH: POST `/inventory`

##### Get an inventory by an inventory id

- PATH: GET `/inventory/{string:id} `

##### List all inventory

- PATH: GET `/inventory`

##### Query an inventory by a given attribute

- By product id:  GET `/inventory?product-id={int:pid}`
- By condition:  GET `/inventory?condition={string:condition} `
- By condition and product id: GET `/inventory?condition={string:condition}&product-id={int:pid} `
- By need restock or not: GET `/inventory?restock={bool:needRestock} `
- By restock level: GET `/inventory?restock-level={int:restock-level-value} `
- By availability: GET `/inventory?available={bool:isAvailable}`
- By availability and product id: GET /inventory?available={bool:isAvailable}&product-id={int:pid}

##### Delete an inventory

- PATH: DELETE `/inventory/{string:id} `

##### Disable an inventory

- PATH: PUT `/inventory/{int:product-id}/disable`

##### Update an inventory

- PATH: PUT `/inventory/{string:id}`

## View App with UI
https://nyu-inventory-service-f19.mybluemix.net/

## View Product with UI
https://nyu-inventory-service-f19-prod.mybluemix.net/

## Delivery Pipeline
https://cloud.ibm.com/devops/pipelines/5ef0d78c-44b1-4115-aa5d-8283a9ae61db?env_id=ibm:yp:us-south

## Swagger Documentation
https://nyu-inventory-service-f19-prod.mybluemix.net/apidocs/index.html
