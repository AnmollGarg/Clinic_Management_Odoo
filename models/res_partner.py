from odoo import models, fields,api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_doctor = fields.Boolean(string='Is Doctor', default=False, help="Indicates if the partner is a doctor.")
    is_tenant = fields.Boolean(string='Is Tenant', default=False, help="Indicates if the partner is a tenant.")
    is_receptionist = fields.Boolean(string='Is Receptionist', default=False, help="Indicates if the partner is a receptionist.")
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        help="Gender of the partner"
    )

    is_patient = fields.Boolean(string='Is Patient')
    age = fields.Integer()
    partner_blood_group = fields.Char(string='Blood Group')

