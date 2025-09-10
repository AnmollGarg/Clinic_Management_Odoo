from odoo import models, fields, api
from odoo.exceptions import UserError


class ClinicManagement(models.Model):
    _name = 'clinic.management'
    _description = 'Clinic Management'

    name = fields.Char(string='Clinic Name', required=True)
    address = fields.Text(string='Address')
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email Address')

