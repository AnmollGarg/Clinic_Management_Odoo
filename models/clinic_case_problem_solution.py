from odoo import models, fields, api
from odoo.exceptions import UserError

class ClinicCaseProblemSolution(models.Model):
    _name = 'clinic.case.problem.solution'
    _description = 'Clinic Case Problem and Solution'

    case_id = fields.Many2one('clinic.case', string='Case')
    problem = fields.Char( required=True, tracking=True)
    solution = fields.Char( required=True, tracking=True)
    description_ids = fields.Char(string='Description', required=True, tracking=True)