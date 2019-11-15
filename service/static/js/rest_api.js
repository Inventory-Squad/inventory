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

    // ****************************************
    // Create an Inventory
    // ****************************************

    $("#create-btn").click(function () {

        var product_id = $("#product_id").val();
        var quantity = $("#quantity").val();
        var restock_level = $("#restock_level").val();
        var condition = $("#condition").val();
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
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an Inventory
    // ****************************************

    $("#retrieve-btn").click(function () {

        var inventory_id = $("#inventory_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/inventory/" + inventory_id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
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
            flash_message("Inventory has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#inventory_id").val("");
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

        if (product_id) {
            if (queryString.length > 0) {
                queryString += '&product_id=' + product_id
            } else {
                queryString += 'product_id=' + product_id
            }
        }
        if (quantity) {
            if (queryString.length > 0) {
                queryString += '&quantity=' + quantity
            } else {
                queryString += 'quantity=' + quantity
            }
        }
        if (restock_level) {
            if (queryString.length > 0) {
                queryString += '&restock_level=' + restock_level
            } else {
                queryString += 'restock_level=' + restock_level
            }
        }
        if (condition) {
            if (queryString.length > 0) {
                queryString += '&condition=' + condition
            } else {
                queryString += 'condition=' + condition
            }
        }
        if (available) {
            if (queryString.length > 0) {
                queryString += '&available=' + available
            } else {
                queryString += 'available=' + available
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/inventory?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:20%">ID</th>'
            header += '<th style="width:10%">Product Id</th>'
            header += '<th style="width:10%">Quantity</th>'
            header += '<th style="width:10%">Restock Level</th>'
            header += '<th style="width:10%">Condition</th></tr>'
            header += '<th style="width:10%">Available </th></tr>'
            $("#search_results").append(header);
            var firstInventory = "";
            for(var i = 0; i < res.length; i++) {
                var inventory = res[i];
                var row = "<tr><td>"+inventory._id+"</td><td>"+inventory.product_id+"</td><td>"+inventory.quantity+"</td><td>"+inventory.restock_level+"</td></tr>"+inventory.condition+"</td></tr>"+inventory.available+"</td></tr>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstInventory = inventory;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstInventory != "") {
                update_form_data(firstInventory)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
