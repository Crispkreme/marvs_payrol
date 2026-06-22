function format_hours(hours) {
    let total_minutes = Math.round(Number(hours || 0) * 60);

    let h = Math.floor(total_minutes / 60);
    let m = total_minutes % 60;

    return `${h}h ${m}m`;
}


// =====================================
// DOLE OVERTIME PAY
// =====================================
function compute_dole_pay(frm, d) {

    let hr = flt(d.hourly_rate || 0);

    let reg_ot = flt(d.overtime_hrs);
    let night_ot = flt(d.night_overtime_hrs);
    let rest_ot = flt(d.rest_day_ot);
    let reg_hol_ot = flt(d.regular_holiday_ot);
    let spec_hol_ot = flt(d.special_holiday_ot);

    let regular_ot_pay = reg_ot * hr * 1.25;
    let night_ot_pay = night_ot * hr * 1.25 * 1.10;
    let rest_day_ot_pay = rest_ot * hr * 1.30;
    let regular_holiday_ot_pay = reg_hol_ot * hr * 2.00;
    let special_holiday_ot_pay = spec_hol_ot * hr * 1.30;

    let total_overtime_pay =
        regular_ot_pay +
        night_ot_pay +
        rest_day_ot_pay +
        regular_holiday_ot_pay +
        special_holiday_ot_pay;

    console.log("====================================");
    console.log("🇵🇭 DOLE OT PAY");
    console.log("Regular OT:", regular_ot_pay);
    console.log("Night OT:", night_ot_pay);
    console.log("Rest Day OT:", rest_day_ot_pay);
    console.log("Regular Holiday OT:", regular_holiday_ot_pay);
    console.log("Special Holiday OT:", special_holiday_ot_pay);
    console.log("TOTAL OT PAY:", total_overtime_pay);

    frm.set_value("overtime_pay", total_overtime_pay);

    return total_overtime_pay;
}


// =====================================
// NET PAY
// =====================================
// =====================================
// NET PAY
// =====================================
function compute_net_pay(frm, d) {

    // Government contributions from Employee Doctype
    let sss = flt(d.sss_contribution || 0);
    let philhealth = flt(d.philhealth_contribution || 0);
    let pagibig = flt(d.pagibig_contribution || 0);
    let tin = flt(d.tin_contribution || 0);

    // Show contributions in Payroll Entry
    frm.set_value("sss_deduction", sss);
    frm.set_value("philhealth_deduction", philhealth);
    frm.set_value("pagibig_deduction", pagibig);
    frm.set_value("tin_deduction", tin);

    // Gross income
    let gross_pay =
        flt(d.basic_salary || 0) +
        flt(d.allowance || 0) +
        flt(frm.doc.overtime_pay || 0);

    // Late deduction
    let late_minutes = flt(d.late || 0) / 60;
    let late_deduction = (flt(d.hourly_rate || 0)) * late_minutes;

    // Absence deduction
    let absent_deduction =
        flt(d.daily_rate || 0) *
        flt(d.absent || 0);

    // Government deductions (already computed in Employee)
    let government_deduction =
        sss +
        philhealth +
        pagibig +
        tin;

    // Total deduction
    let total_deduction =
        government_deduction +
        late_deduction +
        absent_deduction;

    // Net pay
    let net_pay = gross_pay - total_deduction;

    // Set fields
    frm.set_value("deduction", total_deduction);
    frm.set_value("net_pay", net_pay);

    // Logs
    console.log("====================================");
    console.log("💰 PAYROLL COMPUTATION");

    console.log("Basic Salary:", d.basic_salary);
    console.log("Allowance:", d.allowance);
    console.log("Overtime Pay:", frm.doc.overtime_pay);

    console.log("SSS:", sss);
    console.log("PhilHealth:", philhealth);
    console.log("Pag-IBIG:", pagibig);
    console.log("TIN:", tin);

    console.log("Late Deduction:", late_deduction);
    console.log("Absent Deduction:", absent_deduction);

    console.log("Government Deduction:", government_deduction);
    console.log("Total Deduction:", total_deduction);

    console.log("NET PAY:", net_pay);
}

frappe.ui.form.on("PMS-Payroll Entry", {

    employee(frm) {

        if (!frm.doc.employee) return;

        frappe.call({
            method: "marvs_payrol.payroll_management_system.doctype.pms_payroll_entry.pms_payroll_entry.get_payroll_inputs",
            args: {
                employee: frm.doc.employee
            },

            callback: function (r) {

                let d = r.message || {};

                // ===================================
                // BASIC INFORMATION
                // ===================================
                frm.set_value("employee_name", d.employee_name);
                frm.set_value("employment_status", d.employment_status);
                frm.set_value("basic_pay", d.basic_salary || 0);
                frm.set_value("allowance", d.allowance || 0);

                frm.set_value("hourly_rate", d.hourly_rate || 0);
                frm.set_value("daily_rate", d.daily_rate || 0);

                // ===================================
                // WORK HOURS
                // ===================================
                let work_hours =
                    flt(d.day_shift_hrs) +
                    flt(d.night_shift_hrs) +
                    flt(d.regular_holiday) +
                    flt(d.special_holiday) +
                    flt(d.rest_day);

                let overtime_hours =
                    flt(d.overtime_hrs) +
                    flt(d.night_overtime_hrs) +
                    flt(d.regular_holiday_ot) +
                    flt(d.special_holiday_ot) +
                    flt(d.rest_day_ot);

                let late = flt(d.late);
                let absent = flt(d.absent);

                // ===================================
                // RAW VALUES
                // ===================================
                frm.set_value("total_work_hr", work_hours);
                frm.set_value("total_overtime_min", overtime_hours * 60);
                frm.set_value("total_late_min", late);
                frm.set_value("total_absent", absent);

                // ===================================
                // DISPLAY VALUES
                // ===================================
                frm.set_value(
                    "total_work_hr_display",
                    format_hours(work_hours)
                );

                frm.set_value(
                    "total_overtime_display",
                    format_hours(overtime_hours)
                );

                frm.set_value(
                    "total_late_display",
                    `${late} min`
                );

                frm.set_value(
                    "total_absent_display",
                    `${absent} day(s)`
                );

                // ===================================
                // GOVERNMENT CONTRIBUTIONS
                // (already computed in Employee)
                // ===================================
                frm.set_value("sss_deduction", d.sss_contribution || 0);
                frm.set_value("philhealth_deduction", d.philhealth_contribution || 0);
                frm.set_value("pagibig_deduction", d.pagibig_contribution || 0);
                frm.set_value("tin_deduction", d.tin_contribution || 0);

                // ===================================
                // DOLE OVERTIME PAY
                // ===================================
                compute_dole_pay(frm, d);

                // ===================================
                // NET PAY
                // ===================================
                compute_net_pay(frm, d);

                console.log("====================================");
                console.log("👤 Employee:", d.employee_name);
                console.log("💰 Basic Salary:", d.basic_salary);
                console.log("💰 Allowance:", d.allowance);

                console.log("🏛 SSS:", d.sss_contribution);
                console.log("🏛 PhilHealth:", d.philhealth_contribution);
                console.log("🏛 Pagibig:", d.pagibig_contribution);
                console.log("🏛 TIN:", d.tin_contribution);

                console.log("🕒 Work Hours:", format_hours(work_hours));
                console.log("⏱ OT Hours:", format_hours(overtime_hours));
                console.log("⏰ Late:", late);
                console.log("❌ Absent:", absent);

                console.log("💵 OT Pay:", frm.doc.overtime_pay);
                console.log("💵 Net Pay:", frm.doc.net_pay);
            }
        });

    }

});