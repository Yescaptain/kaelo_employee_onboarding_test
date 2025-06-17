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
    for row in reader:
            # Validate required fields
            if not row.get('ID Number') or not row.get('Full Name') or not row.get('Date of Birth'):
                errors.append(f"Row {row}: Missing required fields.")
                continue

            # Standardize date_of_birth format (DD/MM/YYYY)
            try:
                date_of_birth = datetime.strptime(row['Date of Birth'], '%d/%m/%Y').date()
            except ValueError:
                errors.append(f"Row {row}: Invalid date format. Use DD/MM/YYYY.")
                continue

            # Check for duplicate employee_number entries
            if self.env['employee.onboarding'].search([('employee_number', '=', row['Employee Number'])]):
                errors.append(f"Row {row}: Duplicate Employee Number.")
                continue

            # Create employee.onboarding record
            try:
                self.env['employee.onboarding'].create({
                    'full_name': row['Full Name'],
                    'id_number': row['ID Number'],
                    'date_of_birth': date_of_birth,
                    'employee_number': row['Employee Number'],
                    'email': row['Email Address'],
                })
                created += 1
            except Exception as e:
                errors.append(f"Row {row}: {str(e)}")

        # Output summary of successes and failures
        if errors:
            error_message = "\n".join(errors)
            raise UserError(f"Import Summary:\nSuccess: {created}\nFailures: {len(errors)}\n\nErrors:\n{error_message}")
        else:
            raise UserError(f"Import Summary:\nSuccess: {created}\nFailures: 0")

        
