frappe.pages['point-of-sale'].on_page_load = function(wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Point of Sale'),
		single_column: true
	});

	frappe.require('assets/js/point-of-sale.min.js', function() {
		// by malik
		// fix update profile tidak brubah ktika update company => file pos_controller.js
		// ctt: malas build ulang
		$.extend(erpnext.PointOfSale.Controller.prototype, {
			// init_order_summary() {
			// 	this.order_summary = new erpnext.PointOfSale.PastOrderSummary({
			// 		wrapper: this.$components_wrapper,
			// 		events: {
			// 			get_frm: () => this.frm,
		
			// 			process_return: (name) => {
			// 				this.recent_order_list.toggle_component(false);
			// 				frappe.db.get_doc('POS Invoice', name).then((doc) => {
			// 					frappe.run_serially([
			// 						// () => this.make_return_invoice(doc),
			// 						() => this.cart.load_invoice(),
			// 						() => this.item_selector.toggle_component(true)
			// 					]);
			// 				});
			// 			},
			// 			edit_order: (name) => {
			// 				this.recent_order_list.toggle_component(false);
			// 				frappe.run_serially([
			// 					() => this.frm.refresh(name),
			// 					() => this.frm.call('reset_mode_of_payments'),
			// 					() => this.cart.load_invoice(),
			// 					() => this.item_selector.toggle_component(true)
			// 				]);
			// 			},
			// 			delete_order: (name) => {
			// 				frappe.model.delete_doc(this.frm.doc.doctype, name, () => {
			// 					this.recent_order_list.refresh_list();
			// 				});
			// 			},
			// 			new_order: () => {
			// 				frappe.run_serially([
			// 					() => frappe.dom.freeze(),
			// 					() => this.make_new_invoice(),
			// 					() => this.item_selector.toggle_component(true),
			// 					() => frappe.dom.unfreeze(),
			// 				]);
			// 			}
			// 		}
			// 	})
			// },
            create_opening_voucher: function(){
				const me = this;
				const table_fields = [
					{
						fieldname: "mode_of_payment", fieldtype: "Link",
						in_list_view: 1, label: "Mode of Payment",
						options: "Mode of Payment", reqd: 1
					},
					{
						fieldname: "opening_amount", fieldtype: "Currency",
						in_list_view: 1, label: "Opening Amount",
						options: "company:company_currency",
						change: function () {
							dialog.fields_dict.balance_details.df.data.some(d => {
								if (d.idx == this.doc.idx) {
									d.opening_amount = this.value;
									dialog.fields_dict.balance_details.grid.refresh();
									return true;
								}
							});
						}
					}
				];
				const fetch_pos_payment_methods = () => {
					const pos_profile = dialog.fields_dict.pos_profile.get_value();
					if (!pos_profile) return;
					frappe.db.get_doc("POS Profile", pos_profile).then(({ payments }) => {
						dialog.fields_dict.balance_details.df.data = [];
						payments.forEach(pay => {
							const { mode_of_payment } = pay;
							dialog.fields_dict.balance_details.df.data.push({ mode_of_payment, opening_amount: '0' });
						});
						dialog.fields_dict.balance_details.grid.refresh();
					});
				}
				const dialog = new frappe.ui.Dialog({
					title: __('Create POS Opening Entry'),
					static: true,
					fields: [
						{
							fieldtype: 'Link', label: __('Company'), default: frappe.defaults.get_default('company'),
							options: 'Company', fieldname: 'company', reqd: 1
						},
						{
							fieldtype: 'Link', label: __('POS Profile'),
							options: 'POS Profile', fieldname: 'pos_profile', reqd: 1,
							get_query: () => {
								return {
									query: 'erpnext.accounts.doctype.pos_profile.pos_profile.pos_profile_query',
									filters: { company: dialog.fields_dict.company.get_value() }
								}
							},
							onchange: () => fetch_pos_payment_methods()
						},
						{
							fieldname: "balance_details",
							fieldtype: "Table",
							label: "Opening Balance Details",
							cannot_add_rows: false,
							in_place_edit: true,
							reqd: 1,
							data: [],
							fields: table_fields
						}
					],
					primary_action: async function({ company, pos_profile, balance_details }) {
						if (!balance_details.length) {
							frappe.show_alert({
								message: __("Please add Mode of payments and opening balance details."),
								indicator: 'red'
							})
							return frappe.utils.play_sound("error");
						}
	
						// filter balance details for empty rows
						balance_details = balance_details.filter(d => d.mode_of_payment);
	
						const method = "erpnext.selling.page.point_of_sale.point_of_sale.create_opening_voucher";
						const res = await frappe.call({ method, args: { pos_profile, company, balance_details }, freeze:true });
						!res.exc && me.prepare_app_defaults(res.message);
						dialog.hide();
					},
					primary_action_label: __('Submit')
				});
				dialog.show();
			}
        });

		// by malik
		// permintaan drw ubah tampilan customer
		$.extend(erpnext.PointOfSale.ItemCart.prototype, {
			update_customer_section() {
				const me = this;
				const { customer, customer_name, email_id='', mobile_no='', image } = this.customer_info || {};
		
				if (customer) {
					this.$customer_section.html(
						`<div class="customer-details">
							<div class="customer-display">
								${this.get_customer_image()}
								<div class="customer-name-desc">
									<div class="customer-name">${customer_name}</div>
									${get_customer_description()}
								</div>
								<div class="reset-customer-btn" data-customer="${escape(customer)}">
									<svg width="32" height="32" viewBox="0 0 14 14" fill="none">
										<path d="M4.93764 4.93759L7.00003 6.99998M9.06243 9.06238L7.00003 6.99998M7.00003 6.99998L4.93764 9.06238L9.06243 4.93759" stroke="#8D99A6"/>
									</svg>
								</div>
							</div>
						</div>`
					);
				} else {
					// reset customer selector
					this.reset_customer_selector();
				}
		
				function get_customer_description() {
					if (!email_id && !mobile_no) {
						return `<div class="customer-desc">${__('Click to add email / phone')}</div>`;
					} else if (email_id && !mobile_no) {
						return `<div class="customer-desc">${email_id}</div>`;
					} else if (mobile_no && !email_id) {
						return `<div class="customer-desc">${mobile_no}</div>`;
					} else {
						return `<div class="customer-desc">${email_id} - ${mobile_no}</div>`;
					}
				}
		
			},
			toggle_customer_info(show) {
				if (show) {
					const { customer, no_rm_patient } = this.customer_info || {};
		
					this.$cart_container.css('display', 'none');
					this.$customer_section.css({
						'height': '100%',
						'padding-top': '0px'
					});
					this.$customer_section.find('.customer-details').html(
						`<div class="header">
							<div class="label">Contact Details</div>
							<div class="close-details-btn">
								<svg width="32" height="32" viewBox="0 0 14 14" fill="none">
									<path d="M4.93764 4.93759L7.00003 6.99998M9.06243 9.06238L7.00003 6.99998M7.00003 6.99998L4.93764 9.06238L9.06243 4.93759" stroke="#8D99A6"/>
								</svg>
							</div>
						</div>
						<div class="customer-display">
							${this.get_customer_image()}
							<div class="customer-name-desc">
								<div class="customer-name">${no_rm_patient || customer}</div>
								<div class="customer-desc"></div>
							</div>
						</div>
						<div class="customer-fields-container">
							<div class="customer_name-field"></div>
							<div class="email_id-field"></div>
							<div class="mobile_no-field"></div>
							<div class="loyalty_program-field"></div>
							<div class="loyalty_points-field"></div>
						</div>
						<div class="transactions-label">Recent Transactions</div>`
					);
					// transactions need to be in diff div from sticky elem for scrolling
					this.$customer_section.append(`<div class="customer-transactions"></div>`);
		
					this.render_customer_fields();
					this.fetch_customer_transactions();
		
				} else {
					this.$cart_container.css('display', 'flex');
					this.$customer_section.css({
						'height': '',
						'padding-top': ''
					});
		
					this.update_customer_section();
				}
			},
			render_customer_fields() {
				const $customer_form = this.$customer_section.find('.customer-fields-container');
		
				const dfs = [
				{
					fieldname: 'customer_name',
					label: __('Customer Name'),
					fieldtype: 'Data',
					placeholder: __("Enter customer's name"),
					read_only: 1
				},
				{
					fieldname: 'email_id',
					label: __('Email'),
					fieldtype: 'Data',
					options: 'email',
					placeholder: __("Enter customer's email")
				},{
					fieldname: 'mobile_no',
					label: __('Phone Number'),
					fieldtype: 'Data',
					placeholder: __("Enter customer's phone number")
				},{
					fieldname: 'loyalty_program',
					label: __('Loyalty Program'),
					fieldtype: 'Link',
					options: 'Loyalty Program',
					placeholder: __("Select Loyalty Program")
				},{
					fieldname: 'loyalty_points',
					label: __('Loyalty Points'),
					fieldtype: 'Data',
					read_only: 1
				}];
		
				const me = this;
				dfs.forEach(df => {
					this[`customer_${df.fieldname}_field`] = frappe.ui.form.make_control({
						df: { ...df,
							onchange: handle_customer_field_change,
						},
						parent: $customer_form.find(`.${df.fieldname}-field`),
						render_input: true,
					});
					this[`customer_${df.fieldname}_field`].set_value(this.customer_info[df.fieldname]);
				})
		
				function handle_customer_field_change() {
					const current_value = me.customer_info[this.df.fieldname];
					const current_customer = me.customer_info.customer;
		
					if (this.value && current_value != this.value && this.df.fieldname != 'loyalty_points') {
						frappe.call({
							method: 'erpnext.selling.page.point_of_sale.point_of_sale.set_customer_info',
							args: {
								fieldname: this.df.fieldname,
								customer: current_customer,
								value: this.value
							},
							callback: (r) => {
								if(!r.exc) {
									me.customer_info[this.df.fieldname] = this.value;
									frappe.show_alert({
										message: __("Customer contact updated successfully."),
										indicator: 'green'
									});
									frappe.utils.play_sound("submit");
								}
							}
						});
					}
				}
			},
			fetch_customer_details(customer) {
				if (customer) {
					return new Promise((resolve) => {
						frappe.db.get_value('Customer', customer, ["customer_name", "email_id", "mobile_no", "image", "loyalty_program", "no_rm_patient"]).then(({ message }) => {
							const { loyalty_program } = message;
							// if loyalty program then fetch loyalty points too
							if (loyalty_program) {
								frappe.call({
									method: "erpnext.accounts.doctype.loyalty_program.loyalty_program.get_loyalty_program_details_with_points",
									args: { customer, loyalty_program, "silent": true },
									callback: (r) => {
										const { loyalty_points, conversion_factor } = r.message;
										if (!r.exc) {
											this.customer_info = { ...message, customer, loyalty_points, conversion_factor };
											resolve();
										}
									}
								});
							} else {
								this.customer_info = { ...message, customer };
								resolve();
							}
						});
					});
				} else {
					return new Promise((resolve) => {
						this.customer_info = {}
						resolve();
					});
				}
			},
			show_discount_control() {
				this.$add_discount_elem.css({ 'padding': '0px', 'border': 'none' });
				this.$add_discount_elem.html(
					`<div class="add-discount-field"></div>`
				);
				const me = this;
				const frm = me.events.get_frm();
				let discount = frm.doc.additional_discount_percentage;
		
				this.discount_field = frappe.ui.form.make_control({
					df: {
						label: __('Discount'),
						fieldtype: 'Data',
						placeholder: ( discount ? discount + '%' :  __('Enter discount percentage.') ),
						input_class: 'input-xs',
						onchange: function() {
							if (flt(this.value) != 0) {
								frappe.model.set_value(frm.doc.doctype, frm.doc.name, 'additional_discount_percentage', flt(this.value));
								me.hide_discount_control(this.value);
							} else {
								frappe.model.set_value(frm.doc.doctype, frm.doc.name, 'additional_discount_percentage', 0);
								me.$add_discount_elem.css({
									'border': '1px dashed var(--gray-500)',
									'padding': 'var(--padding-sm) var(--padding-md)'
								});
								me.$add_discount_elem.html(`${me.get_discount_icon()} ${__('Add Discount')}`);
								me.discount_field = undefined;
							}
						},
					},
					parent: this.$add_discount_elem.find('.add-discount-field'),
					render_input: true,
				});
				this.discount_field.toggle_label(false);
				this.discount_field.set_focus();
			}
		})
		
		// by malik
		// autentikasi klinik manager
		$.extend(erpnext.PointOfSale.PastOrderSummary.prototype, {
			clinic_manager_auth(callback){
				const dialog = new frappe.ui.Dialog({
					title: __("Clinic Manager Auth"),
					fields: [
						{
							fieldname: "username",
							fieldtype: "Data",
							label: "Username",
							reqd: 1,
						},
						{
							fieldname: "password",
							fieldtype: "Password",
							label: "Password",
							reqd: 1,
						}
					],
					primary_action: function(data) {
						frappe.call({
							method: "addons.addons.doctype.clinic_manager.clinic_manager.validate_clinic_manager",
							args: {
								'username': data.username,
								'password': data.password
							},
							callback: (r) => {
								dialog.hide()

								callback && callback()
							}
						});
					},
					primary_action_label: __("Submit")
				})
				
				dialog.show()
			},
			bind_events() {
				this.$summary_container.on('click', '.return-btn', () => {
					var me = this
					this.clinic_manager_auth(function() {
						me.events.process_return(me.doc.name);
						me.toggle_component(false);
						me.$component.find('.no-summary-placeholder').css('display', 'flex');
						me.$summary_wrapper.css('display', 'none');
					})
				});
		
				this.$summary_container.on('click', '.edit-btn', () => {
					this.events.edit_order(this.doc.name);
					this.toggle_component(false);
					this.$component.find('.no-summary-placeholder').css('display', 'flex');
					this.$summary_wrapper.css('display', 'none');
				});
		
				this.$summary_container.on('click', '.delete-btn', () => {
					var me = this
					this.clinic_manager_auth(function() {
						me.events.delete_order(me.doc.name);
						me.show_summary_placeholder();
					})
				});
		
				// this.$summary_container.on('click', '.delete-btn', () => {
				// 	this.events.delete_order(this.doc.name);
				// 	this.show_summary_placeholder();
				// 	// this.toggle_component(false);
				// 	// this.$component.find('.no-summary-placeholder').removeClass('d-none');
				// 	// this.$summary_wrapper.addClass('d-none');
				// });
		
				this.$summary_container.on('click', '.new-btn', () => {
					this.events.new_order();
					this.toggle_component(false);
					this.$component.find('.no-summary-placeholder').css('display', 'flex');
					this.$summary_wrapper.css('display', 'none');
				});
		
				this.$summary_container.on('click', '.email-btn', () => {
					this.email_dialog.fields_dict.email_id.set_value(this.customer_email);
					this.email_dialog.show();
				});
		
				this.$summary_container.on('click', '.print-btn', () => {
					this.print_receipt();
				});
			}
		})

		$.extend(erpnext.PointOfSale.ItemSelector.prototype, {
			get_item_html(item) {
				const me = this;
				// eslint-disable-next-line no-unused-vars
				const { item_image, serial_no, batch_no, barcode, actual_qty, stock_uom, price_list_rate } = item;
				const precision = flt(price_list_rate, 2) % 1 != 0 ? 2 : 0;
				let indicator_color;
				let qty_to_display = actual_qty;
		
				if (item.is_stock_item) {
					indicator_color = (actual_qty > 10 ? "green" : actual_qty <= 0 ? "red" : "orange");
		
					if (Math.round(qty_to_display) > 999) {
						qty_to_display = Math.round(qty_to_display)/1000;
						qty_to_display = qty_to_display.toFixed(1) + 'K';
					}
				} else {
					indicator_color = '';
					qty_to_display = '';
				}
		
				function get_item_image_html() {
					if (!me.hide_images && item_image) {
						return `<div class="item-qty-pill">
									<span class="indicator-pill whitespace-nowrap ${indicator_color}">${qty_to_display}</span>
								</div>
								<div class="flex items-center justify-center h-32 border-b-grey text-6xl text-grey-100">
									<img
										onerror="cur_pos.item_selector.handle_broken_image(this)"
										class="h-full" src="${item_image}"
										alt="${frappe.get_abbr(item.item_name)}"
										style="object-fit: cover;">
								</div>`;
					} else {
						return `<div class="item-qty-pill">
									<span class="indicator-pill whitespace-nowrap ${indicator_color}">${qty_to_display}</span>
								</div>
								<div class="item-display abbr">${frappe.get_abbr(item.item_name)}</div>`;
					}
				}
		
				return (
					`<div class="item-wrapper"
						data-item-code="${escape(item.item_code)}" data-serial-no="${escape(serial_no)}"
						data-batch-no="${escape(batch_no)}" data-uom="${escape(stock_uom)}"
						data-rate="${escape(price_list_rate || 0)}"
						title="${item.item_name}">
		
						${get_item_image_html()}
		
						<div class="item-detail">
							<div class="item-name">
								${frappe.ellipsis(item.item_name, 18)}
							</div>
							<div class="item-rate">${format_currency(price_list_rate, item.currency, precision) || 0}</div>
						</div>
					</div>`
				);
			}
		})

		wrapper.pos = new erpnext.PointOfSale.Controller(wrapper);
		window.cur_pos = wrapper.pos;
	});
};