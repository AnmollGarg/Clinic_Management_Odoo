import { Component, mount } from "@odoo/owl";
import { useRouter } from "./router";
import { Dashboard } from "./Dashboard";
import { Cases } from "./Cases";
import { Appointments } from "./Appointments";

export class App extends Component {
    static template = "clinic_management.App";
    static components = { Dashboard, Cases, Appointments };
    
    setup() {
        this.router = useRouter();
    }
}

mount(App, document.getElementById("app"));