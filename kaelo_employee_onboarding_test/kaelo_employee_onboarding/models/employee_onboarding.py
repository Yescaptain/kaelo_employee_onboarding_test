from odoo import api, fields, models

class EmployeeOnboarding(models.Model):
    _name = 'employee.onboarding'
    _description = 'Employee Onboarding'

    full_name = fields.Char(string='Full Name', required=True)
    id_number = fields.Char(string='ID Number', required=True)
    date_of_birth = fields.Date(string='Date of Birth')
    employee_number = fields.Char(string='Employee Number', required=True)
    email = fields.Char(string='Email Address', required=True)

    _sql_constraints = [
        ('unique_full_name', 'unique(full_name)', 'The full name must be unique!'),
        ('unique_id_number', 'unique(id_number)', 'The ID number must be unique!'),
        ('unique_employee_number', 'unique(employee_number)', 'The Employee Number must be unique!'),
        ('unique_email', 'unique(email)', 'The Email address must be unique!'),
    ]
    # create a view,action and menu for this model as well
