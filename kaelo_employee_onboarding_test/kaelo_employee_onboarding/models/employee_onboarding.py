from odoo import api, fields, models

class EmployeeOnboarding(models.Model):
    _name = 'employee.onboarding'
    _description = 'Employee Onboarding'

    full_name = fields.Char(string='Full Name', required=True)
    id_number = fields.Char(string='ID Number', required=True)
    date_of_birth = fields.Date(string='Date of Birth', required=True)
    employee_number = fields.Char(string='Employee
    # create a view,action and menu for this model as well
