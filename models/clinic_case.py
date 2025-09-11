from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo import Command

class ClinicCase(models.Model):
    _name = 'clinic.case'
    _description = 'Clinic Case'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'case_id'

    is_paid = fields.Boolean(string='Paid',tracking = True)
    invoice_created = fields.Boolean(default=False, tracking=True)
    patient_id = fields.Many2one('res.partner',string='Patient',domain=[('is_patient', '=', True)],tracking=True,ondelete='set null')
    case_id = fields.Char(readonly=True,tracking=True,)
    appointment_reference = fields.Many2one('clinic.appointment',tracking=True,required = True,domain=[('stage', '=', 'confirm')],help="Reference to the confirmed appointment")
    gender_type = fields.Selection([('child', 'Child'), ('adult', 'Adult'), ('old' , 'Old')],compute='_compute_gender_type',tracking=True)
    case_start_date = fields.Date(required=True,tracking=True,default=fields.Date.today,readonly =True)
    case_closed_date = fields.Date(tracking=True,compute='_compute_case_closed_date',help = "Date when the case was closed")
    doctor_name = fields.Many2one('res.users',required=True,tracking=True,ondelete='restrict',domain=[('is_doctor', '=', True)])
    responsible_person = fields.Many2one('res.users',required=True,tracking=True,ondelete='restrict')
    stage = fields.Selection([('draft', 'Draft'),('confirmed', 'Confirmed'),('done', 'Done'),('cancelled', 'Cancelled')],tracking=True,default='draft',required=True)
    age = fields.Integer(related='patient_id.age',tracking=True,help="Age of the patient")
    problem_solution_ids = fields.One2many('clinic.case.problem.solution', 'case_id', string='Problem and Solution', tracking=True, required = True)
    medicines_ids = fields.One2many('clinic.case.medicines', 'case_id', string='Medicines', tracking=True, required =True)
    case_number = fields.Char(tracking=True)
    clinic_id = fields.Many2one('clinic.config',string='Clinic',ondelete='set null',tracking=True,)
    followup_for_appointment_id = fields.Many2one('clinic.appointment',related='appointment_reference.followup_for_appointment_id',readonly=True)



    # prevent deletion of done cases
    def unlink(self):
        if self.filtered(lambda rec: rec.stage == 'done'):
            raise UserError("You cannot delete a case that is marked as done.")
        return super().unlink()

    # set case_id and validate appointment stage
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('case_id') or vals.get('case_id') == 'New':
                vals['case_id'] = self.env['ir.sequence'].next_by_code('clinic.case') or 'New'
        records = super(ClinicCase, self).create(vals_list)
        for rec in records:
            if rec.appointment_reference and rec.appointment_reference.stage != 'confirm':
                rec.appointment_reference = False
        return records

    def action_confirm(self):
        self.write({'stage': 'confirmed'})

    def action_cancel(self):
        self.write({'stage': 'cancelled'})

    def action_reset_to_draft(self):
        self.write({'stage': 'draft'})

    def print_patient_case_report(self):
        return self.env.ref('clinic_management.patient_case_report_action').report_action(self)

    #Calculate the gender type based on age
    @api.depends('age')
    def _compute_gender_type(self):
        for rec in self:
            if rec.age < 18:
                rec.gender_type = 'child'
            elif 18 <= rec.age < 60:
                rec.gender_type = 'adult'
            elif rec.age >= 60:
                rec.gender_type = 'old'
            else:
                rec.gender_type = False


    @api.onchange('appointment_reference')
    def _onchange_appointment_reference(self):
        if self.appointment_reference:

            if self.appointment_reference.doctor_name:
                self.doctor_name = self.appointment_reference.doctor_name
            else:
                self.doctor_name = False

            if self.appointment_reference.responsible:
                self.responsible_person = self.appointment_reference.responsible
            else:
                self.responsible_person = False

            if self.appointment_reference.patient_id:
                self.patient_id = self.appointment_reference.patient_id
            else:
                self.patient_id = False

            if self.appointment_reference.clinic_id:
                self.clinic_id = self.appointment_reference.clinic_id
            else:
                self.clinic_id = False

    @api.depends('stage')
    def _compute_case_closed_date(self):
        for rec in self:
            rec.case_closed_date = fields.Date.today() if rec.stage == 'done' else False

    def action_done(self):
        self.ensure_one()
        if self.stage != 'confirmed':
            raise UserError(self.env._("You can only create invoices for confirmed cases."))
        if not self.medicines_ids:
            raise UserError(self.env._("No medicines to invoice."))

        sale_order_obj = self.env['sale.order']
        account_move_obj = self.env['account.move']

        # Check if a sale order or invoice already exists for this case
        existing_sale_order = sale_order_obj.search([
            ('origin', '=', self.case_id),
            ('state', '!=', 'cancel')
        ], limit=1)
        
        existing_invoice = account_move_obj.search([
            ('ref', '=', self.case_id),
            ('move_type', '=', 'out_invoice'),
            ('state', '!=', 'cancel')
        ], limit=1)

        if existing_invoice:
            self.write({'invoice_created': True, 'stage': 'done'})
            return {
                'name': 'Patient Invoice',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': existing_invoice.id,
                'type': 'ir.actions.act_window',
            }
        
        if existing_sale_order:
            invoice = existing_sale_order._create_invoices()
            invoice.action_post()
            self.write({'invoice_created': True, 'stage': 'done'})
            return {
                'name': 'Patient Invoice',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': invoice.id,
                'type': 'ir.actions.act_window',
            }

        zero_quantity_medicines = self.medicines_ids.filtered(lambda m: m.product_quantity <= 0)
        if zero_quantity_medicines:
            raise UserError(self.env._("Please specify a quantity for all medicines before creating an invoice."))

        # Prepare sale order lines
        order_lines = []
        for medicine in self.medicines_ids:
            order_lines.append(Command.create({
                'product_id': medicine.product_id.id,
                'name': medicine.product_description or medicine.product_id.name,
                'product_uom_qty': medicine.product_quantity,
                'price_unit': medicine.product_price,
            }))

        # Add doctor fees
        doctor_fees = 0.0
        if self.appointment_reference and self.appointment_reference.doctor_fees:
            doctor_fees = self.appointment_reference.doctor_fees
        if doctor_fees:
            doctor_fees_product = self.env.ref('clinic_management.product_doctor_fees')
            order_lines.append(Command.create({
                'product_id': doctor_fees_product.id,
                'name': 'Doctor Fees',
                'product_uom_qty': 1,
                'price_unit': doctor_fees,
            }))

        # Create sale order with order lines in one go
        sale_order = sale_order_obj.create({
            'partner_id': self.patient_id.id,
            'origin': self.case_id,
            'date_order': fields.Datetime.now(),
            'order_line': order_lines,
        })

        sale_order.action_confirm()
        invoice = sale_order._create_invoices()
        invoice.action_post()

        self.message_post(
            body=f"Sale order and invoice created for {self.case_id}.",
            subtype_id=self.env.ref('mail.mt_note').id
        )

        self.invoice_created = True
        self.stage = 'done'

        return {
            'name': 'Patient Invoice',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'type': 'ir.actions.act_window',
        }

    @api.constrains('problem_solution_ids', 'medicines_ids')
    def _check_required_one2many(self):
        for rec in self:
            if not rec.problem_solution_ids:
                raise ValidationError("At least one Problem and Solution entry is required.")
            if not rec.medicines_ids:
                raise ValidationError("At least one Medicine entry is required.")