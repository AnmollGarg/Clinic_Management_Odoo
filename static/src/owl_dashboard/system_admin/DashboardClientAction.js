/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useRouter } from "./router";

class DashboardClientAction extends Component {
    static template = "clinic_management.App";
    
    setup() {
        this.router = useRouter();
    }
}
registry.category("actions").add("clinic_management.Dashboard", DashboardClientAction);