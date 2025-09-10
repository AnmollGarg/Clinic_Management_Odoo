import { useState } from "@odoo/owl";
import { Dashboard } from "./Dashboard";
import { Cases } from "./Cases";
import { Appointments } from "./Appointments";

const routes = {
    dashboard: Dashboard,
    cases: Cases,
    appointments: Appointments,
};

export function useRouter() {
    const state = useState({
        current: "dashboard"
    });

    function navigate(page) {
        state.current = page;
    }

    function getCurrentComponent() {
        return routes[state.current] || Dashboard;
    }

    return {
        state,
        navigate,
        getCurrentComponent,
    };
}