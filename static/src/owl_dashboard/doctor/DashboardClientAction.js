/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useRouter } from "./router";

class DashboardClientAction extends Component {
    static template = "clinic_management.DoctorApp";

    setup() {
        this.router = useRouter();
    }
}
registry.category("actions").add("doctor_dashboard", DashboardClientAction);