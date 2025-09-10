import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

export class Cases extends Component {
    static template = "clinic_management.CasesPage";
    
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
            
            // Fetch cases data
            this.state.totalCases = await this.orm.searchCount("clinic.case", []);
            this.state.openCases = await this.orm.searchCount("clinic.case", [["stage", "in", ["draft", "confirmed"]]]);
            this.state.completedCases = await this.orm.searchCount("clinic.case", [["stage", "=", "done"]]);
            
            // Fetch cases with related data
            const cases = await this.orm.searchRead(
                "clinic.case",
                [],
                [
                    "id", "case_id", "patient_id", "doctor_name", "case_start_date", "case_closed_date", "stage", "is_paid",
                    "problem_solution_ids", "medicines_ids"
                ],
                {
                    order: "case_start_date desc",
                    limit: 50
                }
            );

            // Fetch all problem solutions and medicines for these cases
            const caseIds = cases.map(c => c.id);

            // Problem Solutions
            const problemSolutions = await this.orm.searchRead(
                "clinic.case.problem.solution",
                [["case_id", "in", caseIds]],
                ["id", "problem", "solution", "description_ids", "case_id"]
            );

            // Medicines
            const medicines = await this.orm.searchRead(
                "clinic.case.medicines",
                [["case_id", "in", caseIds]],
                ["id", "product_id", "product_name", "product_description", "product_quantity", "product_UoM", "product_price", "sub_total", "case_id"]
            );

            // Attach related data to cases
            for (const c of cases) {
                c.problem_solutions = problemSolutions.filter(ps => ps.case_id[0] === c.id);
                c.medicines = medicines.filter(med => med.case_id[0] === c.id);
            }

            this.state.cases = cases;

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

            this.state.patients = await this.orm.searchRead(
                "res.partner",
                [["is_patient", "=", true]],
                ["id", "name", "email", "phone"]
            );
        });

        this.onNewCase = () => {
            this.actionService.doAction({
                type: "ir.actions.act_window",
                res_model: "clinic.case",
                view_mode: "form",
                views: [[false, "form"]],
                target: "current",
                context: {
                    default_doctor_name: session.uid,
                },
            });
        };

        this.onEditCase = (caseId) => {
            this.actionService.doAction({
                type: "ir.actions.act_window",
                res_model: "clinic.case",
                res_id: caseId,
                view_mode: "form",
                views: [[false, "form"]],
                target: "current",
            });
        };
    }
}