from odoo import models, fields, api


class ClinicWorkingTime(models.Model):
    _name = 'clinic.working.time'
    _description = 'Clinic Working Time'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Working Time Name', required=True, tracking=True)
    average_hour_per_day = fields.Float(string='Average Hour Per Day', required=True, tracking=True)
    appointment_time = fields.Integer(
        string='Appointment Time',
        required=True,
        help="Duration of each appointment in minutes (e.g., 30 for 30 minutes)",
        tracking=True
    )
    break_between_appointments = fields.Integer(
        string='Break Between Appointments',
        required=True,
        help="Break time between appointments in minutes",
        tracking=True
    )
    slot_per_day_morning = fields.Integer(string='Slots Per Day (Morning)', required=True, help = "Number of appointment slots available in the morning", tracking=True)
    slot_per_day_evening = fields.Integer(string='Slots Per Day (Evening)', required=True, help = "Number of appointment slots available in the evening", tracking=True)
    timezone = fields.Many2one(
        'res.country',
        required=True,
        help="Select the timezone for the clinic's working hours",
        tracking=True
    )

    work_from = fields.Float(string='Work From', required=True, help="Start time of the working day in hours (e.g., 9.0 for 9 AM)", tracking=True)
    work_to = fields.Float(string='Work To', required=True, help="End time of the working day in hours (e.g., 17.0 for 5 PM)", tracking=True)
    working_hours = fields.Float(string='Working Hours', required=False, help="Total working hours per day", compute='_compute_working_hours')
    working_hour_ids = fields.One2many(
        'clinic.working.hour',
        'working_time_id',
        string='Working Hour'
    )

    #compute functions
    @api.depends('work_from', 'work_to')
    def _compute_working_hours(self):
        for record in self:
            if record.work_from and record.work_to:
                record.working_hours = record.work_to - record.work_from
            else:
                record.working_hours = 0.0


class ClinicWorkingHour(models.Model):
    _name = 'clinic.working.hour'
    _description = 'Clinic Working Hour'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, compute='_compute_name', tracking=True)
    day_of_week = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ], string='Day of Week', required=True, tracking =True)
    day_period = fields.Selection([
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('full_day', 'Full Day'),
        ('half_day', 'Half Day'),
        ('custom', 'Custom'),
    ], string='Day Period', required=True, tracking=True, compute ='_compute_day_period')
    work_from = fields.Float(string='Work from', required=True, tracking=True, help = "Start time as 9.5 is 9:30 AM")
    work_to = fields.Float(string='Work to', required=True, tracking=True, help = "End time as 17.5 is 5:30 PM")
    working_time_id = fields.Many2one('clinic.working.time', string='Working Time', ondelete='cascade', tracking=True)
    doctor_name = fields.Many2one('res.users', string='Doctor', domain=[('is_doctor', '=', True)], required=True, tracking=True)

    #compute functions
    @api.depends('day_of_week', 'day_period')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.day_of_week} {record.day_period}"

    @api.depends('day_period')
    def _compute_work_from(self):
        for record in self:
            if record.day_period == 'morning':
                record.work_from = 9.0
            elif record.day_period == 'afternoon':
                record.work_from = 13.0
            elif record.day_period == 'evening':
                record.work_from = 17.0
            else:
                record.work_from = 0.0  

    @api.depends('day_period')
    def _compute_work_to(self):
        for record in self:
            if record.day_period == 'morning':
                record.work_to = 12.0
            elif record.day_period == 'afternoon':
                record.work_to = 16.0
            elif record.day_period == 'evening':
                record.work_to = 20.0
            else:
                record.work_to = 0.0

    @api.depends('work_from', 'work_to')
    def _compute_day_period(self):
        for record in self:
            if record.work_from >= 9.0 and record.work_to <= 12.0:
                record.day_period = 'morning'
            elif record.work_from >= 13.0 and record.work_to <= 16.0:
                record.day_period = 'afternoon'
            elif record.work_from >= 17.0 and record.work_to <= 20.0:
                record.day_period = 'evening'
            elif record.work_from == 9.0 and record.work_to == 17.0:
                record.day_period = 'full_day'
            elif (record.work_from == 9.0 and record.work_to == 12.0) or (record.work_from == 13.0 and record.work_to == 17.0):
                record.day_period = 'half_day'
            else:
                record.day_period = 'custom'

