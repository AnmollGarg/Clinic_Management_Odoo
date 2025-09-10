from odoo import models, fields, api

class AppointmentCancelWizard(models.TransientModel):
    _name = 'appointment.cancel.wizard'
    _description = 'Appointment Cancel Wizard'

    reason = fields.Text(string='Reason', required=True)

    def action_confirm_cancel(self):
        appointment = self.env['clinic.appointment'].browse(self.env.context.get('active_id'))
        appointment.cancel_reason = self.reason
        appointment.stage = 'cancelled'