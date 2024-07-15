// Copyright (c) 2024, DAS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Budget"] = {
	"filters": [
		{
			"fieldname":"fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
			"reqd": 1,
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		if(["budget", "act", "lm", "ly"].includes(column.fieldname)){
			column.fieldtype = data.is_column ? "Data" : "Currency";
		}else if(["act_persen", "lm_persen", "ly_persen"].includes(column.fieldname)){
			column.fieldtype = value || value === 0 ? "Percent" : "Data";
		}

		value = default_formatter(value, row, column, data);
		
		return value;
	},
};
