const requirement_types = {
    1: {
        "id_map": [
            {"form_id": "requirement_cost", "data_id": "cost"},
            {"form_id": "requirement_label", "data_id": "label"}
        ],
        "const_data": [],
        "requirement_type": "BASE",
        "partial": "/partials/requirement_partial/requirement_base.html"
    },
    2: {
        "id_map": [
            {"form_id": "requirement_cost", "data_id": "cost"},
            {"form_id": "requirement_label", "data_id": "label"},
            {"form_id": "requirement_start_datetime", "data_id": "datetime_start"},
            {"form_id": "requirement_end_datetime", "data_id": "datetime_end"}
        ],
        "const_data": [
            {"data": "DATE_RANGE", "data_id": "time_frame_type"}
        ],
        "requirement_type": "TIMEFRAME",
        "partial": "/partials/requirement_partial/requirement_timeframe_date_range.html"
    },
    3: {
        "id_map": [
            {"form_id": "requirement_cost", "data_id": "cost"},
            {"form_id": "requirement_label", "data_id": "label"},
            {"form_id": "requirement_day_of_week_select", "data_id": "day_of_week"}
        ],
        "const_data": [
            {"data": "DAY_OF_WEEK", "data_id": "time_frame_type"}
        ],
        "requirement_type": "TIMEFRAME",
        "partial": "/partials/requirement_partial/requirement_timeframe_day_of_week.html"
    },
    4: {
        "id_map": [
            {"form_id": "requirement_cost", "data_id": "cost"},
            {"form_id": "requirement_label", "data_id": "label"},
            {"form_id": "requirement_start_time", "data_id": "time_start"},
            {"form_id": "requirement_end_time", "data_id": "time_end"}
        ],
        "const_data": [
            {"data": "TIME_RANGE", "data_id": "time_frame_type"}
        ],
        "requirement_type": "TIMEFRAME",
        "partial": "/partials/requirement_partial/requirement_timeframe_time_range.html"
    },
    5: {
        "id_map": [
            {"form_id": "requirement_cost", "data_id": "cost"},
            {"form_id": "requirement_label", "data_id": "label"},
            {"form_id": "requirement_during", "data_id": "during"},
            {"form_id": "requirement_after", "data_id": "after"},
            {"form_id": "requirement_distance", "data_id": "distance"},

        ],
        "const_data": [],
        "requirement_type": "RELATIVE",
        "partial": "/partials/requirement_partial/requirement_relative.html"
    },
    6: {
        "id_map": [
            {"form_id": "requirement_cost", "data_id": "cost"},
            {"form_id": "requirement_label", "data_id": "label"},

            {"form_id": "requirement_total_requirement", "data_id": "total_requirement"},

            {"form_id": "requirement_scale", "data_id": "scale"},
            {"form_id": "requirement_is_rolling", "data_id": "is_rolling"},
            {"form_id": "requirement_start_datetime", "data_id": "start"},

            //Needed if is rolling
            {"form_id": "requirement_length", "data_id": "length"},

            //Needed if not rolling
            {"form_id": "requirement_end_datetime", "data_id": "end"},

        ],
        "const_data": [],
        "requirement_type": "TOTALS",
        "partial": "/partials/requirement_partial/requirement_totals.html"
    }
};

function requirement_get_type_number(requirement) {
    if (requirement === undefined) {
        return -1;
    }

    if (requirement.hasOwnProperty("requirement_type")) {
        switch (requirement.requirement_type) {
            case "BASE":
                return 1;
            case "TIMEFRAME":
                switch (requirement.data.time_frame_type) {
                    case "DATE_RANGE":
                        return 2;
                    case "DAY_OF_WEEK":
                        return 3;
                    case "TIME_RANGE":
                        return 4;
                    default:
                        return -1;
                }
            case "RELATIVE":
                return 5;
            case "TOTALS":
                return 6;
            default:
                return -1;
        }
    }
}

function requirement_load_partial(destination, requirement_type_number, submit_handler, cancel_handler, delete_handler) {
    requirement_type_number = Number(requirement_type_number);
    destination.empty().load(requirement_types[requirement_type_number].partial, function () {
        let partial = $(this);

        if (delete_handler === undefined) {
            partial.find("#requirement_delete").hide();
        } else {
            partial.find("#requirement_delete").off('click').on('click', delete_handler);
        }

        if (requirement_type_number === 3) {
            partial.find("#requirement_day_of_week_select").val('').selectpicker('refresh');
        } else if (requirement_type_number === 4) {
            partial.find("#requirement_start_time").datetimepicker({"format": "LT"});
            partial.find("#requirement_end_time").datetimepicker({"format": "LT"});
        }


        partial.find("#requirement_cancel").off('click').on('click', cancel_handler);
        partial.find("#requirement_submit").off('click').on('click', submit_handler);
    });
}

function requirement_load_partial_with_data(destination, data, submit_handler, cancel_handler, delete_handler) {
    let requirement_type_number = requirement_get_type_number(data);

    destination.empty().load(requirement_types[requirement_type_number].partial, function () {
        let partial = $(this);

        if (data !== undefined) {
            for (let form_data of requirement_types[requirement_type_number]["id_map"]) {
                if (form_data["form_id"].includes("datetime")) {
                    //Handle special case of datetime
                    if (requirement_type_number !== 6) {
                        $("#" + form_data["form_id"], partial).datetimepicker({"date": moment(new Date(data.data[form_data["data_id"]]))});
                    }
                } else if (form_data["form_id"].includes("time")) {
                    //Handle special case of just time
                    $("#" + form_data["form_id"], partial).datetimepicker({
                        "date": (new Date()).toDateString() + " " + data.data[form_data["data_id"]],
                        "format": "LT"
                    });
                } else {
                    if (form_data["data_id"] !== "during" && form_data["data_id"] !== "after" && form_data["data_id"] !== "scale" && form_data["data_id"] !== "is_rolling") {
                        partial.find("#" + form_data["form_id"]).val('' + data.data[form_data["data_id"]]);
                    }
                }
            }

            if (requirement_type_number === 3) {
                partial.find("#requirement_day_of_week_select").selectpicker('val', '' + data.data["day_of_week"]);
            } else if (requirement_type_number === 5) {
                if (data.data["during"] === true) {
                    partial.find('input:radio[name=inlineRadioOptions][value=during]').trigger('click');
                } else {
                    partial.find('input:radio[name=inlineRadioOptions][value=after]').trigger('click');
                }
            } else if (requirement_type_number === 6) {
                //is_rolling, scale checkboxes
                //is_rolling true then there is length
                //start, end

                $("#requirement_is_rolling", partial).prop("checked", data.data["is_rolling"]);
                $("#requirement_scale", partial).prop("checked", data.data["scale"]);
                let start = moment(new Date(data.data["start"]));

                $("#requirement_start_datetime", partial).datetimepicker({"date": start});

                if (data.data["is_rolling"] === true) {
                    let temp_end = start.add(Number(data.data["length"]), 'hours');

                    $("#requirement_end_datetime", partial).datetimepicker({"date": temp_end});
                } else {
                    $("#requirement_end_datetime", partial).datetimepicker({"date": moment(new Date(data.data["end"]))});
                }
            }
        }


        if (delete_handler === undefined) {
            partial.find("#requirement_delete").hide();
        } else {
            partial.find("#requirement_delete").off('click').on('click', delete_handler);
        }

        partial.find("#requirement_cancel").off('click').on('click', cancel_handler);
        partial.find("#requirement_submit").off('click').on('click', submit_handler);
    });
}

function requirement_get_submit_data(requirement_type_number, element) {
    requirement_type_number = Number(requirement_type_number);

    let requirement_template = requirement_types[requirement_type_number];

    let data = {
        "requirement_type": requirement_template["requirement_type"],
        "data": {}
    };

    //store constant data from template
    for (let const_data of requirement_template["const_data"]) {
        data.data[const_data.data_id] = const_data.data;
    }


    for (let form_data of requirement_template["id_map"]) {
        let temp_data = element.find("#" + form_data["form_id"]).val();

        if (temp_data === undefined) {
            data.data[form_data["data_id"]] = temp_data;
        } else if (form_data["form_id"].includes("date")) {
            //Handle special case of datetime or time
            data.data[form_data["data_id"]] = (new Date(temp_data)).toISOString();
        } else {
            data.data[form_data["data_id"]] = temp_data;
        }
    }

    if (requirement_type_number === 5) {
        //Relative
        let is_during = element.find("input[name=inlineRadioOptions]:checked").val() === "during";

        data.data["during"] = is_during;
        data.data["after"] = !is_during;
    }

    if (requirement_type_number === 6) {
         let start = moment(new Date(data.data["start"]));
         let end = moment(new Date(data.data["end"]));

         data.data["scale"] = element.find("#requirement_scale").is(":checked") === true;
         data.data["is_rolling"] = element.find("#requirement_is_rolling").is(":checked") === true;

         if(data.data["is_rolling"]) {
            data.data["length"] = moment.duration(end.diff(start)).asHours();
         }
    }
    console.log("Getting Data:");
    console.log(data);

    return data;
}

function requirement_get_requirements(entity_id, success_callback) {
    $.ajax({
        url: '/api/v1/entity/' + entity_id + '/requirement',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
    }).done(function (data) {
        success_callback(data["requirement"]);
    });

}
