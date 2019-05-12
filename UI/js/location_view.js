function location_view_update() {
    $('#location_view').load('../partials/location_partial.html', function () {

        jQuery.get("api/v1/location", function (locations) {

            console.log(locations);

            locations.location.forEach(function (location) {
                console.log(location)
            });

            //document.getElementById("shift_table_body").innerHTML = output;
        });
    });
}

function update_location(location_id, location_label) {
    $.ajax({
        url: '/api/v1/location/' + location_id,
        type: 'PUT',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({
            "location_label": location_label
        })
    }).always(function(data){
        alert(data);
    });
}

function create_location(location_label) {
    $.ajax({
        url: '/api/v1/location',
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({
            "location_label": location_label
        })
    }).always(function (data) {
        alert(data)
    });
}

function delete_location(location_id) {
    $.ajax({
        url: '/api/v1/location/' + location_id,
        type: 'DELETE',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({})
    }).always(function (data) {
        alert(data);
    });
}