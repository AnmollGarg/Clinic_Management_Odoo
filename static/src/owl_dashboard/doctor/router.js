import { useState } from "@odoo/owl";
import { DoctorDashboard } from "./DoctorDashboard";
import { DoctorCase } from "./DoctorCase";
import { DoctorPatients } from "./DoctorPatients"; // Import

const routes = {
    dashboard: DoctorDashboard,
    doctor_cases: DoctorCase,
    patients: DoctorPatients, // Add
}

export function useRouter() {
    const state = useState({
        current: "dashboard"
    });

    function navigate(page) {
        state.current = page;
    }

    function getCurrentComponent() {
        return routes[state.current] || DoctorDashboard;
    }

    return {
        state,
        navigate,
        getCurrentComponent,
    };
}