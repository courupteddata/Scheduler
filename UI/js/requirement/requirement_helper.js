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
        "requirement_type": "TIMEFRAME"
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
        "requirement_type": "TIMEFRAME"
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
        "requirement_type": "RELATIVE"
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
        "requirement_type": "TOTALS"
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
