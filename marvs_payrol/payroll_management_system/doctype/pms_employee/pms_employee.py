# Copyright (c) 2026, Marvin Ramos and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PMSEmployee(Document):

    def before_insert(self):
        if not self.user:
            self.user = frappe.session.user

    def validate(self):
        self.full_name = " ".join(filter(None, [
            self.first_name,
            self.middle_name,
            self.last_name
        ]))