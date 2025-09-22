from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('monitor_dashboard/', views.monitor_dashboard, name='monitor_dashboard'),
    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('citizen_dashboard/', views.citizen_dashboard, name='citizen_dashboard'),

    # Citizen specific URLs
    path('citizen/profile/', views.citizen_profile, name='citizen_profile'),
    path('citizen/taxes/', views.citizen_taxes, name='citizen_taxes'),
    path('citizen/schemes_enrolled/', views.citizen_schemes_enrolled, name='citizen_schemes_enrolled'),
    path('citizen/land_records/', views.citizen_land_records, name='citizen_land_records'),
    path('citizen/vaccinations/', views.citizen_vaccinations, name='citizen_vaccinations'),

    path('households/', views.households, name='households'),
    
    path('citizens/', views.citizens, name='citizens'),
    
    path('land_records/', views.land_records, name='land_records'),
    
    path('welfare_schemes_enrollment/', views.welfare_schemes_enrollment, name='welfare_schemes_enrollment'),
    
    path('taxes/', views.taxes, name='taxes'),
    
    path('assets/', views.assets, name='assets'),
    
    path('expenditures/', views.expenditures, name='expenditures'),
    
    path('vaccinations/', views.vaccinations, name='vaccinations'),

    path('census_data/', views.census_data, name='census_data'),

    path('monitor/households/', views.monitor_households, name='monitor_households'),
    
    path('monitor/citizens/', views.monitor_citizens, name='monitor_citizens'),
    
    path('monitor/land_records/', views.monitor_land_records, name='monitor_land_records'),
    
    path('monitor/welfare_schemes_enrollment/', views.monitor_welfare_schemes_enrollment, name='monitor_welfare_schemes_enrollment'),
    
    path('monitor/taxes/', views.monitor_taxes, name='monitor_taxes'),
    
    path('monitor/assets/', views.monitor_assets, name='monitor_assets'),
    
    path('monitor/expenditures/', views.monitor_expenditures, name='monitor_expenditures'),
    
    path('monitor/vaccinations/', views.monitor_vaccinations, name='monitor_vaccinations'),




    path('register/', views.register, name='register'),
    path('register/government-monitor/', views.government_monitor_register, name='government_monitor_register'),
    path('register/panchayat/', views.panchayat_employee_check, name='panchayat_employee_check'),
    path('register/panchayat/<str:citizen_id>/', views.panchayat_employee_register, name='panchayat_employee_register'),
    path('register/citizen/', views.citizen_register, name='citizen_register'),

    path('dashboard/manage-government-monitors/', views.manage_government_monitors, name='manage_government_monitors'),
    path('dashboard/manage-panchayat-employees/', views.manage_panchayat_employees, name='manage_panchayat_employees'),
    path('dashboard/manage-households/', views.manage_households, name='manage_households'),
    path('dashboardmanage-citizens/', views.manage_citizens, name='manage_citizens'),
    path('dashboard/manage-land-records/', views.manage_land_records, name='manage_land_records'),
    path('dashboard/manage-welfare-schemes-enrollment/', views.manage_welfare_schemes_enrollment, name='manage_welfare_schemes_enrollment'),
    path('dashboard/manage-taxes/', views.manage_taxes, name='manage_taxes'),
    path('dashboard/manage-assets/', views.manage_assets, name='manage_assets'),
    path('dashboard/manage-expenditures/', views.manage_expenditures, name='manage_expenditures'),
    path('dashboard/manage-vaccinations/', views.manage_vaccinations, name='manage_vaccinations'),
    path('welfare_schemes/', views.manage_welfare_schemes, name='manage_welfare_schemes'),
    path('welfare_schemes/delete/<int:scheme_id>/', views.delete_welfare_scheme, name='delete_welfare_scheme'),


    
   

    path('logout/', views.logout_view, name='logout'),
]
