from odoo import models, fields


class ClinicManagement(models.Model):
    _name = 'clinic.management'
    _description = 'Clinic Management'

    name = fields.Char( required=True)
    address = fields.Text()
    phone = fields.Char()
    email = fields.Char()

