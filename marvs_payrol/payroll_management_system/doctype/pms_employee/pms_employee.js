// Copyright (c) 2026, Marvin Ramos and contributors
// For license information, please see license.txt

frappe.ui.form.on("PMS-Employee", {
	refresh(frm) {
        toggle_contract_date(frm);
    },

    not_contractual(frm) {
        toggle_contract_date(frm);
    }
});

function toggle_contract_date(frm) {
    if (frm.doc.not_contractual) {
        frm.set_df_property('contract_end_date', 'read_only', 1);
        frm.set_df_property('contract_end_date', 'reqd', 0);

        // optional: clear value
        // frm.set_value('contract_end_date', null);
    } else {
        frm.set_df_property('contract_end_date', 'read_only', 0);
    }
}
