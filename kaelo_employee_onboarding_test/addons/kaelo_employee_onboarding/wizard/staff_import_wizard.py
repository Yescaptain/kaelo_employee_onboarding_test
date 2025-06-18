import base64
import csv
import io
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StaffImportWizard(models.TransientModel):
    _name = 'employee.onboarding.import'
    _description = 'Import Employee Onboarding'

    csv_file = fields.Binary('CSV File', required=True)
    filename = fields.Char('Filename')

    def action_import(self):
        self.ensure_one()

        print("Starting CSV import...", flush=True)
        data = base64.b64decode(self.csv_file or b'')
        f = io.StringIO(data.decode('utf-8'))
        reader = csv.DictReader(f)
        print(f"CSV header fields detected: {reader.fieldnames}", flush=True)

        errors = []
        created = 0

        Employee = self.env['employee.onboarding']

        existing_emp_numbers = set(Employee.search([]).mapped('employee_number'))
        existing_full_names = set(Employee.search([]).mapped('full_name'))
        existing_id_numbers = set(Employee.search([]).mapped('id_number'))
        existing_emails = set(Employee.search([]).mapped('email'))

        seen_emp_numbers = set()
        seen_full_names = set()
        seen_id_numbers = set()
        seen_emails = set()

        for idx, row in enumerate(reader, start=2):
            print(f"Processing line {idx}: {row}", flush=True)

            full_name = (row.get('full_name') or '').strip()
            id_number = (row.get('id_number') or '').strip()
            date_of_birth_text = (row.get('date_of_birth') or '').strip()
            employee_number = (row.get('employee_number') or '').strip()
            email = (row.get('email') or '').strip()

            if not full_name or not id_number or not date_of_birth_text:
                err_msg = f"Line {idx}: Missing required fields (Full Name, ID Number, or Date of Birth)."
                print(f"ERROR: {err_msg}", flush=True)
                errors.append(err_msg)
                continue

            try:
                dob_obj = datetime.strptime(date_of_birth_text, '%d/%m/%Y')
                date_of_birth = dob_obj.strftime('%Y-%m-%d')
            except ValueError:
                err_msg = f"Line {idx}: Invalid date format '{date_of_birth_text}', expected DD/MM/YYYY."
                print(f"ERROR: {err_msg}", flush=True)
                errors.append(err_msg)
                continue

            duplicate = False
            if not employee_number:
                err_msg = f"Line {idx}: Employee Number is missing."
                print(f"ERROR: {err_msg}", flush=True)
                errors.append(err_msg)
                duplicate = True
            if employee_number in existing_emp_numbers or employee_number in seen_emp_numbers:
                err_msg = f"Line {idx}: Duplicate employee_number '{employee_number}'."
                print(f"ERROR: {err_msg}", flush=True)
                errors.append(err_msg)
                duplicate = True
            if full_name in existing_full_names or full_name in seen_full_names:
                err_msg = f"Line {idx}: Duplicate full_name '{full_name}'."
                print(f"ERROR: {err_msg}", flush=True)
                errors.append(err_msg)
                duplicate = True
            if id_number in existing_id_numbers or id_number in seen_id_numbers:
                err_msg = f"Line {idx}: Duplicate id_number '{id_number}'."
                print(f"ERROR: {err_msg}", flush=True)
                errors.append(err_msg)
                duplicate = True
            if email and (email in existing_emails or email in seen_emails):
                err_msg = f"Line {idx}: Duplicate email '{email}'."
                print(f"ERROR: {err_msg}", flush=True)
                errors.append(err_msg)
                duplicate = True

            if duplicate:
                print(f"Skipping line {idx} due to duplicates or missing data.", flush=True)
                continue

            # Register to prevent duplicates in this run
            seen_emp_numbers.add(employee_number)
            seen_full_names.add(full_name)
            seen_id_numbers.add(id_number)
            if email:
                seen_emails.add(email)

            try:
                new_rec = Employee.create({
                    'full_name': full_name,
                    'id_number': id_number,
                    'date_of_birth': date_of_birth,
                    'employee_number': employee_number,
                    'email': email,
                })
                created += 1
                print(f"Created employee record ID {new_rec.id} at line {idx}", flush=True)
            except Exception as e:
                err_msg = f"Line {idx}: Failed to create employee record: {str(e)}"
                print(f"ERROR: {err_msg}", flush=True)
                errors.append(err_msg)

        print(f"Import finished: {created} records created, {len(errors)} errors.", flush=True)
        summary = f"Import completed: {created} employees created."
        if errors:
            summary += f"\n\nFailed rows ({len(errors)}):\n" + "\n".join(errors)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Import Completed with Errors'),
                    'message': summary,
                    'sticky': False,
                    'type': 'warning',
                },
            }

        # No errors - success notification + redirect to list
        return {
            'type': 'ir.actions.act_window',
            'name': 'Onboarding Records',
            'res_model': 'employee.onboarding',
            'view_mode': 'tree,form',
            'target': 'current',
            'context': self.env.context,
            'flags': {'initial_mode': 'list'},
            'params': {
                'message': summary,
            }
        }