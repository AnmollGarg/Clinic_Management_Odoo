from odoo import models, fields

class ClinicPatientConsultation(models.Model):
    _name = 'clinic.patient.consultation' 
    _description = 'Clinic Patient Consultation'

    patient_id = fields.Many2one(
        'res.partner',
        string='Patient',
        domain=[('is_patient', '=', True)],
        required=True
    )
    appointment_reference = fields.Char( required=True)
    consultation_date = fields.Datetime(required=True)
    doctor_name = fields.Many2one('res.users',required=True, domain=[('is_doctor', '=', True)])
    responsible_person = fields.Char( required=True)
    gender = fields.Selection(
        related='patient_id.gender',
        readonly=True
    )
    appointment_id = fields.Many2one(
        'clinic.appointment',
        string='Appointment'
    )
    case_id = fields.Many2one(
        'clinic.case',
        string='Case'
    )