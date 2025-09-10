/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

export class DoctorDashboard extends Component {
    static template = "clinic_management.DoctorDashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            appointmentCount: 0,
            caseCount: 0,
            appointments: [],
            cases: [],
            upcomingAppointments: [],
            ongoingAppointments: [],
            outgoingAppointments: [],
            allAppointments: [],
            upcomingCases: [],
            ongoingCases: [],
            outgoingCases: [],
            allCases: [],
            doctorName: session.name,
            loading: true,
        });

        onWillStart(async () => {
            // Appointments
            this.state.appointmentCount = await this.orm.searchCount("clinic.appointment", []);
            this.state.caseCount = await this.orm.searchCount("clinic.case", []);
            const appointments = await this.orm.searchRead(
                "clinic.appointment",
                [],
                ["id", "name", "appointment_date", "patient_id", "doctor_name", "stage"],
                { order: "appointment_date desc", limit: 50 }
            );
            this.state.allAppointments = appointments;
            const now = new Date().toISOString().slice(0, 19);
            this.state.upcomingAppointments = appointments.filter(a => a.appointment_date > now && a.stage !== "done" && a.stage !== "cancelled");
            this.state.ongoingAppointments = appointments.filter(a => a.appointment_date <= now && a.stage === "confirm");
            this.state.outgoingAppointments = appointments.filter(a => a.stage === "done" || a.stage === "cancelled");
            this.state.appointments = appointments.slice(0, 10);

            // Cases
            const cases = await this.orm.searchRead(
                "clinic.case",
                [],
                ["id", "case_id", "patient_id", "doctor_name", "stage", "case_start_date", "case_closed_date"],
                { order: "case_start_date desc", limit: 50 }
            );
            this.state.allCases = cases;
            this.state.upcomingCases = cases.filter(c => !c.case_start_date);
            this.state.ongoingCases = cases.filter(c => c.stage === "open");
            this.state.outgoingCases = cases.filter(c => c.stage === "closed");
            this.state.cases = cases.slice(0, 10);

            this.state.loading = false;
        });

        this.onAddNewCase = (appt) => {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                res_model: "clinic.case",
                view_mode: "form",
                views: [[false, "form"]],
                target: "current",
                context: {
                    default_appointment_reference: appt.id,
                    default_doctor_name: appt.doctor_name && appt.doctor_name[0],
                },
            });
        };
    }

    getStageColor(stage) {
        switch (stage) {
            case "draft": return "gray";
            case "booked": return "blue";
            case "confirm": return "orange";
            case "done": return "green";
            case "cancelled": return "red";
            default: return "gray";
        }
    }
}

