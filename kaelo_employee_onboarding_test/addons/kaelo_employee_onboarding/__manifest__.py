{
    'name': 'Kaelo Employee Onboarding',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Module for employee onboarding and import',
    'author': 'Kaelo',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_onboarding_views.xml',
        'views/staff_import_wizard.xml',
    ],
    'installable': True,
    'application': False,
}