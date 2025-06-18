import re
from datetime import date
from odoo import api, fields, models
from odoo.exceptions import ValidationError

EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

class EmployeeOnboarding(models.Model):
    _name = 'employee.onboarding'
    _description = 'Employee Onboarding'

    full_name = fields.Char(string='Full Name', required=True)
    id_number = fields.Char(string='ID Number', required=True)
    date_of_birth = fields.Date(string='Date of Birth', required=True)
    employee_number = fields.Char(string='Employee Number', required=True)
    email = fields.Char(string='Email Address', required=True)

    @api.constrains('full_name', 'id_number', 'date_of_birth', 'employee_number', 'email')
    def _check_fields(self):
        for record in self:
            # Validate required fields (redundant due to required=True but safe)
            if not record.full_name:
                raise ValidationError("Full Name is required.")
            if not record.id_number:
                raise ValidationError("ID Number is required.")
            if not record.date_of_birth:
                raise ValidationError("Date of Birth is required.")

            # Date of birth must not be in the future
            if record.date_of_birth > date.today():
                raise ValidationError("Date of Birth cannot be in the future.")

            # Validate email format with regex
            if record.email and not re.match(EMAIL_REGEX, record.email):
                raise ValidationError(f"Email '{record.email}' is not valid.")

            # Check uniqueness of fields (excluding current record)
            domain_map = {
                'full_name': record.full_name,
                'id_number': record.id_number,
                'employee_number': record.employee_number,
                'email': record.email,
            }
            for field_name, value in domain_map.items():
                existing = self.search([
                    (field_name, '=', value),
                    ('id', '!=', record.id)
                ], limit=1)
                if existing:
                    raise ValidationError(f"The {field_name.replace('_', ' ').title()} '{value}' must be unique.")