from odoo import models, fields

class ClinicPatient(models.Model):
    _name = 'clinic.patient'
    _description = 'Clinic Patient'

    name = fields.Char(string='Patient Name', required=True)
    email = fields.Char(string='Email')
    image_1920 = fields.Binary("Image", attachment=True)
