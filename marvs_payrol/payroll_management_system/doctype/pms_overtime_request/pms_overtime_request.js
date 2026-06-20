// Copyright (c) 2026, Marvin Ramos and contributors
// For license information, please see license.txt

frappe.ui.form.on("PMS-Overtime Request Request", {

    employee(frm) {

        if (!frm.doc.employee) return;

        frappe.db.get_doc(
            "PMS-Employee",
            frm.doc.employee
        ).then(emp => {

            frm.set_value(
                "employee_name",
                emp.full_name
            );

            frm.set_value(
                "department",
                emp.department
            );

            frm.set_value(
                "position",
                emp.position
            );

        });

    }

});
