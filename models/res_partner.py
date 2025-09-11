from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_doctor = fields.Boolean( default=False, help="Indicates if the partner is a doctor.")
    is_tenant = fields.Boolean( default=False, help="Indicates if the partner is a tenant.")
    is_receptionist = fields.Boolean(default=False, help="Indicates if the partner is a receptionist.")
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        help="Gender of the partner"
    )

    is_patient = fields.Boolean()
    age = fields.Integer()
    partner_blood_group = fields.Char()

