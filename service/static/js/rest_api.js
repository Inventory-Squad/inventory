$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#inventory_id").val(res._id);
        $("#product_id").val(res.product_id);
        $("#quantity").val(res.quantity);
        $("#restock_level").val(res.restock_level);
        $("#condition").val(res.condition);
        $("#available").val(res.quanavailabletity);
        if (res.available == true) {
            $("#available").val("true");
        } else {
            $("#available").val("false");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#inventory_id").val("");
        $("#product_id").val("");
        $("#quantity").val("");
        $("#restock_level").val("");
        $("#condition").val("");
        $("#available").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    function list_all_inventories() {
        var ajax = $.ajax({
            type: "GET",
            url: "/inventory",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            $("#search_results").empty();
            var table = '<table class="table-striped"><tr><thead>'
            table += '<th class="col-md-3 text-center">ID</th>'
            table += '<th class="col-md-2 text-center">Product Id</th>'
            table += '<th class="col-md-1 text-center">Quantity</th>'
            table += '<th class="col-md-2 text-center">Restock Level</th>'
            table += '<th class="col-md-2 text-center">Condition</th>'
            table += '<th class="col-md-2 text-center">Availability</th></tr>'
            table += '</thead><tbody>'
            for(var i = 0; i < res.length; i++) {
                var inventory = res[i];
                table += "<tr ><td>"+inventory._id+"</td><td>"+inventory.product_id+"</td><td>"+inventory.quantity+"</td><td>"+inventory.restock_level+"</td><td>"+inventory.condition+"</td><td>"+inventory.available+"</td></tr>";
            }
            table += '<tbody></table>'
            $("#search_results").append(table);
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    }

    // ****************************************
    // Create an Inventory
    // ****************************************

    $("#create-btn").click(function () {
        var product_id = $("#product_id").val();
        var quantity = $("#quantity").val();
        var restock_level = $("#restock_level").val();
        var condition = $("#condition").val().length > 0 ? $("#condition").val() : "new";
        var available = $("#available").val() == "true";

        var data = {
            "product_id": parseInt(product_id),
            "quantity": parseInt(quantity),
            "restock_level": parseInt(restock_level),
            "condition": condition,
            "available": available
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/inventory",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
            list_all_inventories()
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an Inventory
    // ****************************************

    $("#update-btn").click(function () {

        var inventory_id = $("#inventory_id").val();
        var product_id = $("#product_id").val();
        var quantity = $("#quantity").val();
        var restock_level = $("#restock_level").val();
        var condition = $("#condition").val();
        var available = $("#available").val() == "true";

        var data = {
            "inventory_id": inventory_id,
            "product_id": parseInt(product_id),
            "quantity": parseInt(quantity),
            "restock_level": parseInt(restock_level),
            "condition": condition,
            "available": available
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/inventory/" + inventory_id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Inventory "+ inventory_id +" has been Updated!")
            list_all_inventories()
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // **********************************************
    // Disable a Product
    // **********************************************

    $("#disable-btn").click(function () {
        var product_id = $("#product_id").val();

        var ajax = $.ajax({
                type: "PUT",
                url: "/inventory/" + product_id + "/disable",
                contentType: "application/json",
                data:''
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Product " + product_id +" has been Disabled!")
            list_all_inventories()
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // **********************************************
    // List all Inventory that need to be restocked
    // **********************************************

    $("#restock-list-btn").click(function () {
        var ajax = $.ajax({
                type: "GET",
                url: "/inventory?restock=true",
                contentType: "application/json",
                data: ''
            })
            ajax.done(function(res){
                //alert(res.toSource())
                $("#search_results").empty();
                var table = '<table class="table-striped"><tr><thead>'
                table += '<th class="col-md-3 text-center">ID</th>'
                table += '<th class="col-md-2 text-center">Product Id</th>'
                table += '<th class="col-md-1 text-center">Quantity</th>'
                table += '<th class="col-md-2 text-center">Restock Level</th>'
                table += '<th class="col-md-2 text-center">Condition</th>'
                table += '<th class="col-md-2 text-center">Availability</th></tr>'
                table += '</thead><tbody>'
                for(var i = 0; i < res.length; i++) {
                    var inventory = res[i];
                    table += "<t><td>"+inventory._id+"</td><td>"+inventory.product_id+"</td><td>"+inventory.quantity+"</td><td>"+inventory.restock_level+"</td><td>"+inventory.condition+"</td><td>"+inventory.available+"</td></tr>";
                }
                table += '<tbody></table>'
                $("#search_results").append(table);
                flash_message('GET /inventory?restock=true Success!')
            });

            ajax.fail(function(res){
                flash_message(res.responseJSON.message)
            });

    });

    // ****************************************
    // Retrieve an Inventory
    // ****************************************

    $("#retrieve-btn").click(function () {
        $("#search_results").empty();
        var inventory_id = $("#inventory_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/inventory/" + inventory_id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Inventory "+ inventory_id +" has been Retrieved!")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Inventory
    // ****************************************

    $("#delete-btn").click(function () {
        var inventory_id = $("#inventory_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/inventory/" + inventory_id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Inventory "+ inventory_id +" has been Deleted!")
            list_all_inventories()
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        clear_form_data()
    });


    // ****************************************
    // Search for an Inventory
    // ****************************************

    $("#search-btn").click(function () {
        var product_id = $("#product_id").val();
        var quantity = $("#quantity").val();
        var restock_level = $("#restock_level").val();
        var condition = $("#condition").val();
        var available = $("#available").val() == "true";

        var queryString = ""
        var validQuery = true;

        if (quantity) {
            queryString += 'quantity=' + quantity
            validQuery = false
        }

        if (condition) {
            if (queryString.length > 0) {
                queryString += '&condition=' + condition
                validQuery = false
            } else {
                queryString += 'condition=' + condition
            }
        }

        if (product_id) {
            if( queryString.length == 0) {
                queryString += 'product-id=' + product_id
            } else if (queryString.length > 0) {
                queryString += '&product-id=' + product_id
                if(!condition) {
                    validQuery = false;
                }
            }
        }

        if (restock_level) {
            if (queryString.length > 0) {
                queryString += '&restock-level=' + restock_level
                validQuery = false
            } else {
                queryString += 'restock-level=' + restock_level
            }
        }

        if ($("#available").val()) {
            if (queryString.length > 0) {
                queryString += '&available=' + available
                validQuery = false
            } else {
                queryString += 'available=' + available
            }
        }

        if( validQuery == true ) {
            var ajax = $.ajax({
                type: "GET",
                url: "/inventory?" + queryString,
                contentType: "application/json",
                data: ''
            })

            ajax.done(function(res){
                $("#search_results").empty();
                var table = '<table class="table-striped"><tr><thead>'
                table += '<th class="col-md-3 text-center">ID</th>'
                table += '<th class="col-md-2 text-center">Product Id</th>'
                table += '<th class="col-md-1 text-center">Quantity</th>'
                table += '<th class="col-md-2 text-center">Restock Level</th>'
                table += '<th class="col-md-2 text-center">Condition</th>'
                table += '<th class="col-md-2 text-center">Availability</th>'
                table += '</thead><tbody>'
                for(var i = 0; i < res.length; i++) {
                    var inventory = res[i];
                    table += "<tr><td>"+inventory._id+"</td><td>"+inventory.product_id+"</td><td>"+inventory.quantity+"</td><td>"+inventory.restock_level+"</td><td>"+inventory.condition+"</td><td>"+inventory.available+"</td></tr>";
                }

                table += '<tbody></table>'
                $("#search_results").append(table)
                flash_message('GET /inventory' + (queryString.length > 0 ? '?'+ queryString :'') +' Success! <br>')
            });

            ajax.fail(function(res){
                $("#search_results").empty()
                clear_form_data()
                flash_message(res.responseJSON.message + '<br> Only accept following search request:<br>'+ 'GET /inventory?product-id={product-id}<br>GET /inventory?available={isAvailable}<br>GET /inventory?restock-level={restock-level-value}<br>GET /inventory?condition={condition}<br>GET /inventory?condition={condition}&product-id={product-id}<br>')
            });
        } else {
            invalidSearch(queryString)
        }

    });

    function invalidSearch(queryString) {
        $("#search_results").empty()
        clear_form_data()
        flash_message('GET /inventory?' + queryString + ' Failed! <br> Only accept following search request:<br>'+ 'GET /inventory?product-id={product-id}<br>GET /inventory?available={isAvailable}<br>GET /inventory?restock-level={restock-level-value}<br>GET /inventory?condition={condition}<br>GET /inventory?condition={condition}&product-id={product-id}<br>')
    }

})
