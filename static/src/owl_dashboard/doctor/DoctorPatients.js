/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class DoctorPatients extends Component {
    static template = "clinic_management.DoctorPatients";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            patients: [],
            loading: true,
        });

        onWillStart(async () => {
            const patients = await this.orm.searchRead(
                "res.partner",
                [["is_patient", "=", true]],
                ["id", "name", "email", "phone"]
            );
            this.state.patients = patients;
            this.state.loading = false;
        });
    }
}