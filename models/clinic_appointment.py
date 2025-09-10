from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class ClinicAppointment(models.Model):
    _name = 'clinic.appointment'
    _description = 'Clinic Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    
    name = fields.Char(
        string='Appointment Reference',
        readonly=True,
        tracking=True,
    )
    patient_id = fields.Many2one(
        'res.partner',
        string='Patient',
        tracking=True,
        domain=[('is_patient', '=', True)]
    )

    case_id = fields.Many2one(
        'clinic.case',
        tracking=True,
        string='Related Case',
    )

    related_cases_ids = fields.One2many(
        'clinic.case',
        'appointment_reference',
        string='Related Cases',
        tracking=True,

        help="All cases related to this appointment"
    )
    
    doctor_name = fields.Many2one(
        'res.users',
        string='Doctor Name',
        required=True,
        tracking=True,
        domain="[('is_doctor', '=', True)]",
        help="Select the doctor for the appointment"
    )

    clinic_id = fields.Many2one('clinic.config', string='Clinic', required = True)


    responsible = fields.Many2one(
        'res.users',
        required=True, 
        tracking=True,
        readonly=True,
        default=lambda self: self.env.user,
        help="The user who created this appointment"
    )
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High')
    ], default='0', tracking=True)

    appointment_date = fields.Datetime(
        string='Appointment Date & Time',
        required=True,
        tracking=True,
        default=fields.Datetime.now,
        help="Select the date and time for the appointment"
    )
    appointment_end_date = fields.Datetime(
        string='Appointment End Date & Time',
        required=True,
        help="End date and time for the appointment"
    )
    appointment_duration = fields.Char(
        string='Duration',
        compute='_compute_appointment_duration',
        help="Duration of the appointment in minutes"
    )

    stage = fields.Selection(
        [
            ('draft', 'Draft'),
            ('booked', 'Booked'),
            ('confirm', 'Confirmed'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled')
        ],

        default='draft',
        required=True,
        tracking=True
    )

    cancel_reason = fields.Text(
        string='Cancellation Reason',
        help="Reason for cancelling the appointment",
        tracking=True,
    )

    user_timezone = fields.Char(
        string='User Timezone',
        compute='_compute_user_timezone',
        help="Timezone of the current user"
    )

    is_doctor_available = fields.Boolean(
        string='Doctor Available',
        compute='_compute_is_doctor_available',
        help="Indicates if the doctor is available at the selected time"
    )

    appointment_type = fields.Selection(
        [('fresh', 'Fresh Appointment'), ('followup', 'Follow Up')],
        string='Appointment Type',
        required=True,
        default='fresh',
        tracking=True,
        help="Specify if this is a fresh appointment or a follow-up"
    )

    doctor_fees = fields.Float(
        string='Doctor Fees',
        compute='_compute_doctor_fees',
        help="Appointment fees based on doctor and appointment type"
    )

    followup_for_appointment_id = fields.Many2one(
        'clinic.appointment',
        string='Follow-up For',
        domain="[('patient_id', '=', patient_id), ('stage', '=', 'done'), ('id', '!=', id)]",
        help="Select the original appointment for which this is a follow-up",
    )

    booked_slots_times = fields.Char(
        string='Booked Slots (Time)',
        compute='_compute_booked_slots_times',
        help="All booked time slots for the selected doctor and date"
    )

    @api.depends('doctor_name', 'appointment_date')
    def _compute_booked_slots_times(self):
        for rec in self:
            booked_times = []
            if rec.doctor_name and rec.appointment_date:
                user_date = fields.Datetime.context_timestamp(rec, rec.appointment_date).date()
                appointments = self.env['clinic.appointment'].search([
                    ('doctor_name', '=', rec.doctor_name.id),
                    ('stage', 'in', ['booked', 'confirm', 'done', 'draft']),
                    ('id', '!=', rec.id),
                ])
                for app in appointments:
                    if app.appointment_date:
                        start_dt = fields.Datetime.context_timestamp(rec, app.appointment_date)
                        end_dt = fields.Datetime.context_timestamp(rec, app.appointment_end_date) if app.appointment_end_date else None
                        if start_dt.date() == user_date:
                            start = start_dt.strftime('%H:%M')
                            end = end_dt.strftime('%H:%M') if end_dt else ''
                            booked_times.append(f"{start}-{end}")
            rec.booked_slots_times = ', '.join(booked_times)


    @api.depends('doctor_name', 'clinic_id', 'appointment_type')
    def _compute_doctor_fees(self):
        for rec in self:
            fee = 0.0
            if rec.doctor_name and rec.clinic_id and rec.appointment_type:
                avail = rec.clinic_id.availability_ids.filtered(lambda a: a.doctor_id == rec.doctor_name)
                if avail:
                    if rec.appointment_type == 'fresh':
                        fee = avail[0].doctor_appoitment_fees
                    elif rec.appointment_type == 'followup':
                        fee = avail[0].doctor_appoitment_followup_fees
            rec.doctor_fees = fee

    @api.onchange('case_id')
    def _onchange_case_id(self):
        if self.case_id:
            self.doctor_name = self.case_id.doctor_name
            self.patient_id = self.case_id.patient_id

            if not self.case_id.appointment_reference:
                self.case_id.appointment_reference = self.id
        else:
            self.doctor_name = False
            self.patient_id = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('clinic.appointment') or 'New'
        return super(ClinicAppointment, self).create(vals_list)

    def action_book(self):
        self.write({'stage': 'booked'})

    def action_confirm(self):
        self.write({'stage': 'confirm'})
        for rec in self:
            if rec.case_id and not rec.case_id.appointment_reference:
                rec.case_id.appointment_reference = rec.id

    def action_done(self):
        self.write({'stage': 'done'})

    def action_cancel(self):
        for rec in self:
            if not rec.cancel_reason:
                raise UserError("Please provide a reason for cancellation before cancelling the appointment.")
        self.write({'stage': 'cancelled'})
        for rec in self:
            if rec.case_id and rec.case_id.appointment_reference == rec.id:
                rec.case_id.appointment_reference = False

    def action_reset_to_defaults(self):
        self.write({'stage': 'draft', 'cancel_reason': False})
        for rec in self:
            if rec.case_id and rec.case_id.appointment_reference == rec.id:
                rec.case_id.appointment_reference = False

    def print_patient_appointment_report(self):
        return self.env.ref('clinic_management.patient_appointment_report_action').report_action(self)

    @api.constrains('appointment_date')
    def _check_appointment_date(self):
        for record in self:
            if record.appointment_date:
                user_dt = fields.Datetime.context_timestamp(record, record.appointment_date)
                now = fields.Datetime.context_timestamp(record, datetime.now())
                if user_dt < now:
                    raise UserError(self.env._("You cannot select a past date and time for an appointment."))


    @api.constrains('appointment_date', 'doctor_name', 'appointment_end_date')
    def _check_appointment_overlap(self):
        for record in self:
            if record.appointment_date and record.doctor_name:
                domain = [
                    ('id', '!=', record.id),
                    ('doctor_name', '=', record.doctor_name.id),
                    ('stage', '!=', 'cancelled'),
                    ('appointment_date', '<=', record.appointment_end_date),
                    ('appointment_end_date', '>=', record.appointment_date),
                ]
                overlapping = self.search(domain, limit=1)
                if overlapping:
                    raise UserError(self.env._("This doctor already has an appointment during the selected time slot. Please choose a different time."))

    @api.constrains('appointment_date', 'clinic_id')
    def _check_appointment_within_working_hours(self):
        for record in self:
            if record.appointment_date and record.clinic_id and record.clinic_id.working_time_id:
                dt = fields.Datetime.context_timestamp(record, record.appointment_date)
                hour = dt.hour
                minute = dt.minute
                appointment_hour = hour + minute / 60.0
                work_from = record.clinic_id.working_time_id.work_from
                work_to = record.clinic_id.working_time_id.work_to

                if not (work_from <= appointment_hour < work_to):
                    raise UserError(self.env._("Appointment time must be within clinic working hours: %.2f to %.2f") % (work_from, work_to))

                if record.appointment_end_date:
                    end_dt = fields.Datetime.context_timestamp(record, record.appointment_end_date)
                    end_hour = end_dt.hour + end_dt.minute / 60.0
                    if not (work_from < end_hour <= work_to):
                        raise UserError(self.env._("Appointment end time must be within clinic working hours: %.2f to %.2f") % (work_from, work_to))



    @api.depends('appointment_date')
    def _compute_user_timezone(self):
        for record in self:
            record.user_timezone = record.env.user.tz
            

    @api.depends('appointment_date', 'appointment_end_date')
    def _compute_appointment_duration(self):
        for record in self:
            if record.appointment_date and record.appointment_end_date:
                duration = record.appointment_end_date - record.appointment_date
                minutes = int(duration.total_seconds() // 60)
                record.appointment_duration = f"{minutes} min"
            else:
                record.appointment_duration = ""

    @api.constrains('clinic_id', 'doctor_name')
    def _check_doctor_in_clinic(self):
        for rec in self:
            if rec.clinic_id and rec.doctor_name:
                if rec.doctor_name not in rec.clinic_id.clinic_doctor_id:
                    raise UserError("Selected doctor is not assigned to the selected clinic.")

    @api.depends('appointment_date', 'appointment_end_date', 'doctor_name')
    def _compute_is_doctor_available(self):
        for record in self:
            available = True
            if record.appointment_date and record.doctor_name and record.clinic_id and record.clinic_id.working_time_id:
                dt = fields.Datetime.context_timestamp(record, record.appointment_date)
                weekday = dt.strftime('%A').lower()
                working_hours = record.clinic_id.working_time_id.working_hour_ids.filtered(
                    lambda wh: wh.doctor_name == record.doctor_name and wh.day_of_week == weekday
                )
                if not working_hours:
                    available = False
                else:
                    domain = [
                        ('id', '!=', record.id),
                        ('doctor_name', '=', record.doctor_name.id),
                        ('stage', '!=', 'cancelled'),
                        ('appointment_date', '<=', record.appointment_end_date),
                        ('appointment_end_date', '>=', record.appointment_date),
                    ]
                    overlapping = self.search(domain, limit=1)
                    if overlapping:
                        available = False
            else:
                available = False
            record.is_doctor_available = available

    @api.constrains('appointment_type', 'followup_for_appointment_id')
    def _check_followup_for_required(self):
        for rec in self:
            if rec.appointment_type == 'followup' and not rec.followup_for_appointment_id:
                raise ValidationError("Please select the appointment for which this is a follow-up.")

    @api.constrains('appointment_date', 'doctor_name', 'clinic_id')
    def _check_doctor_working_time(self):
        for rec in self:
            if rec.appointment_date and rec.doctor_name and rec.clinic_id and rec.clinic_id.working_time_id:

                dt = fields.Datetime.context_timestamp(rec, rec.appointment_date)
                weekday = dt.strftime('%A').lower()  
                hour = dt.hour + dt.minute / 60.0


                working_hours = rec.clinic_id.working_time_id.working_hour_ids.filtered(
                    lambda wh: wh.doctor_name == rec.doctor_name and wh.day_of_week == weekday
                )

                available = any(wh.work_from <= hour < wh.work_to for wh in working_hours)
                if not available:
                    raise UserError(self.env._("Doctor %s is not available on %s. Please select a valid time within their working hours.")
                        % (rec.doctor_name.name, weekday.capitalize())
                    )

    def unlink(self):
        done_appointments = self.filtered(lambda rec: rec.stage == 'done')
        if done_appointments:
            raise UserError(self.env._("You cannot delete appointments that are in 'Done' stage."))
        return super(ClinicAppointment, self).unlink()

