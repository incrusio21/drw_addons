frappe.provide("addons.timesheet");

addons.timesheet.timer = function(frm, row, timestamp=0) {
	let dialog = new frappe.ui.Dialog({
		title: __("Timer"),
		fields:
		[
			{"fieldtype": "Data", "label": __("Patient Name"), "fieldname": "patient_name", "read_only": 1},
			{"fieldtype": "Link", "label": __("Therapy Type"), "fieldname": "therapy_type", "options": "Therapy Type"},
			{"fieldtype": "Int", "label": __("Duration"), "fieldname": "duration"},
			{"fieldtype": "Time", "label": __("Start Time"), "fieldname": "start_time"},
			{"fieldtype": "Section Break"},
			{"fieldtype": "HTML", "fieldname": "timer_html"}
		]
	});

	if (row) {
		dialog.set_values({
			'patient_name': row.patient_name,
			'therapy_type': row.therapy_type,
			'duration': row.duration,
			'start_time': frappe.datetime.convert_to_system_tz(row.start_date + " " +row.start_time, false).format(frappe.defaultTimeFormat),
		});
	}
	dialog.get_field("timer_html").$wrapper.append(get_timer_html());
	function get_timer_html() {
		return `
			<div class="stopwatch">
				<span class="hours">00</span>
				<span class="colon">:</span>
				<span class="minutes">00</span>
				<span class="colon">:</span>
				<span class="seconds">00</span>
			</div>
			<div class="playpause text-center">
				<button class= "btn btn-primary btn-start"> ${ __("Start") } </button>
				<button class= "btn btn-primary btn-complete"> ${ __("Complete") } </button>
			</div>
		`;
	}
	addons.timesheet.control_timer(frm, dialog, row, timestamp);
	dialog.show();
};

addons.timesheet.control_timer = function(frm, dialog, row, timestamp=0) {
	var $btn_start = dialog.$wrapper.find(".playpause .btn-start");
	var $btn_complete = dialog.$wrapper.find(".playpause .btn-complete");
	var interval = null;
	var currentIncrement = timestamp;
	var initialised = row ? true : false;
	var clicked = false;
	var flag = true; // Alert only once
	// If row with not completed status, initialize timer with the time elapsed on click of 'Start Timer'.
	if (row) {
		initialised = true;
		$btn_start.hide();
		$btn_complete.show();
		initialiseTimer();
	}
	if (!initialised) {
		$btn_complete.hide();
	}
	$btn_start.click(function(e) {
		if (!initialised) {
			// New activity if no activities found
			var args = dialog.get_values();
			if(!args) return;
			if (frm.doc.time_logs.length <= 1 && !frm.doc.time_logs[0].activity_type && !frm.doc.time_logs[0].from_time) {
				frm.doc.time_logs = [];
			}
			row = frappe.model.add_child(frm.doc, "Timesheet Detail", "time_logs");
			row.activity_type = args.activity_type;
			row.from_time = frappe.datetime.get_datetime_as_string();
			row.project = args.project;
			row.task = args.task;
			row.expected_hours = args.expected_hours;
			row.completed = 0;
			let d = moment(row.from_time);
			if(row.expected_hours) {
				d.add(row.expected_hours, "hours");
				row.to_time = d.format(frappe.defaultDatetimeFormat);
			}
			frm.refresh_field("time_logs");
			frm.save();
		}

		if (clicked) {
			e.preventDefault();
			return false;
		}

		if (!initialised) {
			initialised = true;
			$btn_start.hide();
			$btn_complete.show();
			initialiseTimer();
		}
	});

	// Stop the timer and update the time logged by the timer on click of 'Complete' button
	$btn_complete.click(function() {
		frm.set_value("end_time", frappe.datetime.now_time())
        // var grid_row = cur_frm.fields_dict['time_logs'].grid.get_row(row.idx - 1);
		// var args = dialog.get_values();
		// grid_row.doc.activity_type = args.activity_type;
		// grid_row.doc.project = args.project;
		// grid_row.doc.task = args.task;
		// grid_row.doc.expected_hours = args.expected_hours;
		// grid_row.doc.hours = currentIncrement / 3600;
		// grid_row.doc.to_time = frappe.datetime.now_datetime();
		// grid_row.refresh();
		// frm.save();
		reset();
		dialog.hide();
	});
	function initialiseTimer() {
		interval = setInterval(function() {
			var current = setCurrentIncrement();
			updateStopwatch(current);
		}, 1000);
	}

	function updateStopwatch(increment) {
		var hours = Math.floor(increment / 3600);
		var minutes = Math.floor((increment - (hours * 3600)) / 60);
		var seconds = increment - (hours * 3600) - (minutes * 60);

		// If modal is closed by clicking anywhere outside, reset the timer
		if (!$('.modal-dialog').is(':visible')) {
			reset();
		}
		if(hours > 99999)
			reset();
		if(cur_dialog && cur_dialog.get_value('expected_hours') > 0) {
			if(flag && (currentIncrement >= (cur_dialog.get_value('expected_hours') * 3600))) {
				frappe.utils.play_sound("alert");
				frappe.msgprint(__("Timer exceeded the given hours."));
				flag = false;
			}
		}
		$(".hours").text(hours < 10 ? ("0" + hours.toString()) : hours.toString());
		$(".minutes").text(minutes < 10 ? ("0" + minutes.toString()) : minutes.toString());
		$(".seconds").text(seconds < 10 ? ("0" + seconds.toString()) : seconds.toString());
	}

	function setCurrentIncrement() {
		currentIncrement += 1;
		return currentIncrement;
	}

	function reset() {
		currentIncrement = 0;
		initialised = false;
		clearInterval(interval);
		$(".hours").text("00");
		$(".minutes").text("00");
		$(".seconds").text("00");
		$btn_complete.hide();
		$btn_start.show();
	}
};
