/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

export class Dashboard extends Component {
    setup() {
        this.userName = session.name;
        this.orm = useService("orm");
        this.state = useState({
            appointmentCount: 0,
            patientCount: 0,
            doctorCount: 0,
            doctorName: session.name,
            doctors: [],
            appointments: [],
            patients: [],
        });

        onWillStart(async () => {
            this.state.appointmentCount = await this.orm.searchCount("clinic.appointment", []);
            this.state.patientCount = await this.orm.searchCount("res.partner", [["is_patient", "=", true]]);
            this.state.doctorCount = await this.orm.searchCount("res.users", [["is_doctor", "=", true]]);
            this.state.doctorName = session.name;

            // Fetch list of doctors
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

            this.state.patients= await this.orm.searchRead(
                "res.partner",
                [["is_patient", "=", true]],
                ["id", "name", "email", "phone"]
            );
        });
    }

    formatLocalDatetime(utcString) {
        if (!utcString) return '';
        const date = new Date(utcString.replace(' ', 'T') + 'Z');
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
}
Dashboard.template = "clinic_management.Dashboard";