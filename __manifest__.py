{
    'name': 'Clinic Management',
    'version': '1.0',
    'category': 'Healthcare',
    'summary': 'Manage clinic operations',
    'description': 'Module for managing patients, appointments, cases, and clinic configuration.',
    'depends': ['base', 'sale', 'account', 'mail', 'product'],
    'data': [
        'security/security.xml',
        'security/ir.rule.xml',
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'wizard/appointment_cancel_wizard_views.xml',
        'views/clinic_config_views.xml',
        'views/clinic_working_time_views.xml', 
        'views/clinic_patient_views.xml',
        'views/clinic_appointment_views.xml',
        'views/clinic_case_views.xml',
        'views/clinic_patient_consultation_views.xml',
        'views/dashboard_action.xml',
        'views/clinic_management_menus.xml',

        'data/product_data.xml',
        'data/clinic_management_sequence.xml',
        'views/patient_appointment_receipt.xml',
        'views/patient_case_report.xml',
        
    ],
    'assets': {
        'web.assets_backend': [
            # System admin dashboard - XML
            'clinic_management/static/src/owl_dashboard/system_admin/App.xml',
            'clinic_management/static/src/owl_dashboard/system_admin/Dashboard.xml',
            'clinic_management/static/src/owl_dashboard/system_admin/Cases.xml',
            'clinic_management/static/src/owl_dashboard/system_admin/Appointments.xml',
            
            # System admin dashboard - JS
            'clinic_management/static/src/owl_dashboard/system_admin/router.js',
            'clinic_management/static/src/owl_dashboard/system_admin/app.js',
            'clinic_management/static/src/owl_dashboard/system_admin/Dashboard.js',
            'clinic_management/static/src/owl_dashboard/system_admin/Cases.js',
            'clinic_management/static/src/owl_dashboard/system_admin/Appointments.js',
            'clinic_management/static/src/owl_dashboard/system_admin/DashboardClientAction.js',
            'clinic_management/static/src/owl_dashboard/system_admin/dashboard.scss',
            'clinic_management/static/src/owl_dashboard/system_admin/Appointments.scss',
            'clinic_management/static/src/owl_dashboard/system_admin/Cases.scss',

            # Doctor dashboard - XML
            'clinic_management/static/src/owl_dashboard/doctor/App.xml',
            'clinic_management/static/src/owl_dashboard/doctor/DoctorDashboard.xml', 
            'clinic_management/static/src/owl_dashboard/doctor/DoctorDashboard.scss',
            'clinic_management/static/src/owl_dashboard/doctor/DoctorCase.scss',
            'clinic_management/static/src/owl_dashboard/doctor/DoctorCase.xml',
            'clinic_management/static/src/owl_dashboard/doctor/DoctorPatients.xml',
            'clinic_management/static/src/owl_dashboard/doctor/DoctorPatients.scss',


            # Doctor dashboard - JS
            'clinic_management/static/src/owl_dashboard/doctor/router.js',
            'clinic_management/static/src/owl_dashboard/doctor/app.js',
            'clinic_management/static/src/owl_dashboard/doctor/DoctorDashboard.js',
            'clinic_management/static/src/owl_dashboard/doctor/DashboardClientAction.js',
            'clinic_management/static/src/owl_dashboard/doctor/DoctorCase.js',
            'clinic_management/static/src/owl_dashboard/doctor/DoctorPatients.js',

        ],
    },
    'installable': True,
    'application': True,
}