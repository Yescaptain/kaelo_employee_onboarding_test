from odoo.tests.common import TransactionCase

class TestEmployeeOnboardingImport(TransactionCase):
    def test_import_wizard_creation(self):
        Wizard = self.env['employee.onboarding.import']
        wizard = Wizard.create({'filename': 'staff_list.csv', 'csv_file': b''})
        self.assertTrue(wizard)