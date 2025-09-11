from odoo import models, fields

class ClinicConfig(models.Model):
    _name = 'clinic.config'
    _description = 'Clinic Configuration'
    _rec_name = 'clinic_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    clinic_name = fields.Char(required=True, tracking=True)
    clinic_address = fields.Text(help ="Enter the full address of the clinic", tracking=True)
    clinic_phone = fields.Char(default="", required=True, tracking=True)
    clinic_email = fields.Char(required=True, tracking=True)
    clinic_website = fields.Char(tracking=True)
    clinic_mobile = fields.Char(default="", tracking=True)
    clinic_doctor_id = fields.Many2many(
        'res.users',
        string='Doctor',
        required=True,
        tracking=True,
        domain = [('is_doctor', '=', True)],
    )

    clinic_receptionist_id = fields.Many2one(
        'res.users',
        string='Receptionist',
        required=True,
        tracking=True,
        domain = [('is_receptionist', '=', True)],
    )

    available_time_slots = fields.Selection(
        [('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')],
        required=True,
        default='morning',
        tracking=True,
        help="Select the available time slots for appointments"
    )

    street = fields.Char( required=True, tracking=True)
    street2 = fields.Char( tracking=True)
    city = fields.Char( required=True, tracking=True)
    state_id = fields.Many2one('res.country.state', string='State', required=True, tracking=True)
    zip = fields.Char( required=True, tracking=True)
    country_id = fields.Many2one('res.country', string='Country', required=True, tracking=True)
    logo = fields.Binary()

    availability_ids = fields.One2many(
        'clinic.availability',
        'clinic_config_id',
        tracking=True,
        string='Availability',
    required = True
    )
    working_time_id = fields.Many2one(
        'clinic.working.time',
        string='Working Time',
        help="Select the clinic's working time configuration",
        tracking=True,
    required = True
    )


class ClinicAvailability(models.Model):
    _name = 'clinic.availability'
    _description = 'Clinic Availability'

    # slot_type = fields.Selection(
    #     [('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')],
    #     string='Slot Type',
    #     required=True
    # )
    doctor_id = fields.Many2one('res.users', string='Dr Name', required=True, domain = [('is_doctor', '=', True)])
    doctor_appoitment_fees = fields.Float(required=True, tracking=True)
    doctor_appoitment_followup_fees = fields.Float(required=True, tracking=True)
    clinic_config_id = fields.Many2one('clinic.config', string='Clinic Config', ondelete='cascade')