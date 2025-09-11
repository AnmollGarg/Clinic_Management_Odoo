from odoo import models, fields, api

class ClinicCaseMedicines(models.Model):
    _name = 'clinic.case.medicines'
    _description = 'Clinic Case Medicines'

    case_id = fields.Many2one('clinic.case', string='Case')
  
    product_id = fields.Many2one(
        'product.product',
        string='Medicine',
        required=True,
        domain=[('categ_id', '=', 17)]
    )
    product_name = fields.Char()
    product_description = fields.Text()
    product_quantity = fields.Integer(required=True)
    product_UoM = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
    )
    product_price = fields.Monetary(
        required=True,
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True
    )


    sub_total = fields.Monetary(
        compute='_compute_sub_total',
        currency_field='currency_id'
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.product_price = rec.product_id.lst_price
                rec.product_description = rec.product_id.description or rec.product_id.name
                rec.product_name = rec.product_id.name 
                rec.product_UoM = rec.product_id.uom_id
            else:
                rec.product_price = 0.0
                rec.product_description = ''
                rec.product_name = '' 
                rec.product_UoM = False

    def _compute_sub_total(self):
        for rec in self:
            rec.sub_total = rec.product_quantity * rec.product_price

    def print_patient_appointment_report(self):
        return self.env.ref('clinic_management.patient_appointment_report_action').report_action(self)