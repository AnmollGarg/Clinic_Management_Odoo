import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

export class Appointments extends Component {
    setup() {
        this.userName = session.name;
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.state = useState({
            appointmentCount: 0,
            patientCount: 0,
            doctorCount: 0,
            totalCases: 0,
            openCases: 0,
            completedCases: 0,
            doctorName: session.name,
            doctors: [],
            appointments: [],
            patients: [],
            cases: [],
        });

        onWillStart(async () => {
            this.state.appointmentCount = await this.orm.searchCount("clinic.appointment", []);
            this.state.patientCount = await this.orm.searchCount("res.partner", [["is_patient", "=", true]]);
            this.state.doctorCount = await this.orm.searchCount("res.users", [["is_doctor", "=", true]]);
            this.state.doctorName = session.name;

            this.state.totalCases = await this.orm.searchCount("clinic.case", []);
            this.state.openCases = await this.orm.searchCount("clinic.case", [["stage", "in", ["draft", "confirmed"]]]);
            this.state.completedCases = await this.orm.searchCount("clinic.case", [["stage", "=", "done"]]);

            this.state.cases = await this.orm.searchRead(
                "clinic.case",
                [],
                ["id", "case_id", "patient_id", "doctor_name", "case_start_date", "case_closed_date", "stage", "is_paid"],
                {
                    order: "case_start_date desc",
                    limit: 50
                }
            );

            this.state.doctors = await this.orm.searchRead(
                "res.users",
                [["is_doctor", "=", true]],
                ["id", "name", "email", "phone"]
            );

            this.state.appointments = await this.orm.searchRead(
                "clinic.appointment",
                [],
                ["id", "name", "appointment_date", "patient_id", "doctor_name", "stage", "appointment_end_date"],
                {
                    order: "appointment_date desc"
                }
            );

            this.state.patients = await this.orm.searchRead(
                "res.partner",
                [["is_patient", "=", true]],
                ["id", "name", "email", "phone"]
            );
        });

        this.onNewAppointment = () => {
            this.actionService.doAction({
                type: "ir.actions.act_window",
                res_model: "clinic.appointment",
                view_mode: "form",
                views: [[false, "form"]],
                target: "current",
                context: {
                    default_doctor_name: session.uid,
                },
            });
        };

        this.onEditAppointment = (appointmentId) => {
            this.actionService.doAction({
                type: "ir.actions.act_window",
                res_model: "clinic.appointment",
                res_id: appointmentId,
                view_mode: "form",
                views: [[false, "form"]],
                target: "current",
            });
        };

        this.onNewCase = (appointmentId) => {
            this.actionService.doAction({
                type: "ir.actions.act_window",
                res_model: "clinic.case",
                view_mode: "form",
                views: [[false, "form"]],
                target: "current",
                context: {
                    default_appointment_reference: appointmentId,
                    default_doctor_name: session.uid,
                },
            });
        };
    }

    formatDateTime(dateTime) {
        if (!dateTime) return "";
        const date = new Date(dateTime.replace(' ', 'T') + 'Z');
        return date.toLocaleString(undefined, {
            year: 'numeric',
            month: 'numeric',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        });
    }

    getStageClass(stage) {
        const classes = {
            'draft': 'badge bg-secondary',
            'booked': 'badge bg-info',
            'confirm': 'badge bg-primary',
            'done': 'badge bg-success',
            'cancelled': 'badge bg-danger'
        };
        return classes[stage] || 'badge bg-secondary';
    }
}

Appointments.template = "clinic_management.AppointmentsPage";