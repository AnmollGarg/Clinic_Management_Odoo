import { Component, mount } from "@odoo/owl";
import { useRouter } from "./router";
import { DoctorDashboard } from "./DoctorDashboard";


export class App extends Component {
    static template = "clinic_management.DoctorApp";
   static components = { DoctorDashboard };

    setup() {
        this.router = useRouter();
    }
}

mount(App, document.getElementById("doctor_app"));