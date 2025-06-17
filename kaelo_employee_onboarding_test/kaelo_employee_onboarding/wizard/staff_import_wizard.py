import base64, csv, io
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StaffImportWizard(models.TransientModel):
    _name = 'employee.onboarding.import'
    _description = 'Import Employee Onboarding'

    csv_file = fields.Binary('CSV File', required=True)
    filename = fields.Char('Filename')

    def action_import(self):
        data = base64.b64decode(self.csv_file or b'')
        f = io.StringIO(data.decode('utf-8'))
        reader = csv.DictReader(f)
        errors = []
        created = 0
        # complete this import and handling
        Employee = self.env['employee.onboarding']
        # Gather existing employee numbers, full_names, id_numbers, and emails for duplicate check
        existing_emp_numbers = set(Employee.search([]).mapped('employee_number'))
        existing_full_names = set(Employee.search([]).mapped('full_name'))
        existing_id_numbers = set(Employee.search([]).mapped('id_number'))
        existing_emails = set(Employee.search([]).mapped('email'))
        seen_emp_numbers = set()
        seen_full_names = set()
        seen_id_numbers = set()
        seen_emails = set()

        for idx, row in enumerate(reader, start=2):  # header is line 1
            full_name = (row.get('full_name') or '').strip()
            id_number = (row.get('id_number') or '').strip()
            date_of_birth_text = (row.get('date_of_birth') or '').strip()
            employee_number = (row.get('employee_number') or '').strip()
            email = (row.get('email') or '').strip()

            # Validate required fields
            if not full_name or not id_number or not date_of_birth_text:
                errors.append(f"Line {idx}: Missing required fields (Full Name, ID Number, or Date of Birth).")
                continue

            # Validate date format
            try:
                dob_obj = datetime.strptime(date_of_birth_text, '%d/%m/%Y')
                date_of_birth = dob_obj.strftime('%Y-%m-%d')
            except Exception:
                errors.append(f"Line {idx}: Invalid date format for '{date_of_birth_text}' (should be DD/MM/YYYY).")
                continue

            # Duplicate checks: in DB and in current file
            dup = False
            if not employee_number:
                errors.append(f"Line {idx}: Employee Number is missing.")
                dup = True
            if employee_number in existing_emp_numbers or employee_number in seen_emp_numbers:
                errors.append(f"Line {idx}: Duplicate Employee Number '{employee_number}'.")
                dup = True
            if full_name in existing_full_names or full_name in seen_full_names:
                errors.append(f"Line {idx}: Duplicate Full Name '{full_name}'.")
                dup = True
            if id_number in existing_id_numbers or id_number in seen_id_numbers:
                errors.append(f"Line {idx}: Duplicate ID Number '{id_number}'.")
                dup = True
            if email and (email in existing_emails or email in seen_emails):
                errors.append(f"Line {idx}: Duplicate Email '{email}'.")
                dup = True
            if dup:
                continue

            # Register as seen
            seen_emp_numbers.add(employee_number)
            seen_full_names.add(full_name)
            seen_id_numbers.add(id_number)
            if email:
                seen_emails.add(email)

            # Create employee record
            try:
                Employee.create({
                    'full_name': full_name,
                    'id_number': id_number,
                    'date_of_birth': date_of_birth,
                    'employee_number': employee_number,
                    'email': email,
                })
                created += 1
            except Exception as e:
                errors.append(f"Line {idx}: Failed to create employee: {str(e)}.")
                continue

        summary = f"Created {created} employees."
        if errors:
            summary += "\n\nSome rows were skipped:\n"
            summary += "\n".join(errors)

        # Error popup if errors, success notification if only successes
        if errors:
            raise UserError(summary)
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': summary,
                    'sticky': False,
                    'type': 'success',
                }
            }


        
