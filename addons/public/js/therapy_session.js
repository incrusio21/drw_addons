// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Therapy Session', {
    setup: function(frm) {
		frappe.require("/assets/addons/css/therapy_session.css");
		frappe.require("/assets/addons/js/healthcare/timer.js");
    },
    refresh: function(frm) {
        if(!frm.doc.__islocal && frm.doc.docstatus == 0){
            let button = 'Start Timer';
            var row = frm.doc

            var time = frappe.datetime.convert_to_system_tz(row.start_date + " " +row.start_time)

			if ((time <= frappe.datetime.now_datetime())) {
                button = 'Resume Timer';
            }

			frm.add_custom_button(__(button), function() {
				var flag = true;
                // Fetch the row for which from_time is not present

                // Fetch the row for timer where activity is not completed and from_time is before now_time
                
                if (flag && time<= frappe.datetime.now_datetime()) {
                    let timestamp = moment(frappe.datetime.now_datetime()).diff(moment(time),"seconds");
                    addons.timesheet.timer(frm, row, timestamp);
                    flag = false;
                }

				// If no activities found to start a timer, create new
				// if (flag) {
				// 	addons.timesheet.timer(frm, frm.doc);
				// }
			}).addClass("btn-primary");
        }
    }
})