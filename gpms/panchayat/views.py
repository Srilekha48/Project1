from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db import connection
from django.db.utils import OperationalError, DatabaseError
from django.contrib.auth.hashers import check_password
import logging

logger = logging.getLogger(__name__)

def execute_query(query, params=None):
    try:
        with connection.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if query.strip().upper().startswith('SELECT') or 'RETURNING' in query.upper():
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                return cursor.rowcount
    except OperationalError as e:
        logger.error(f"Database connection error: {e}")
        raise
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise


def home(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if role == 'System Admin':
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT username, password FROM system_administrators WHERE username = %s", [username])
                    admin = cursor.fetchone()

                if admin:
                    db_username, db_password = admin

                    # Only allow login if username == "admin" and password == "admin"
                    if db_username == "admin" and db_password == "admin":
                        request.session['user_id'] = db_username  # Store username in session
                        request.session['role'] = role
                        return redirect('admin_dashboard')  # Redirect to admin panel
                    else:
                        messages.error(request, 'Invalid username or password')
                else:
                    messages.error(request, 'User not found')

            except Exception as e:
                messages.error(request, f'Database error: {e}')

        elif role == 'Government Monitor':
            # Handle Government Monitor login
            try:
                query = "SELECT * FROM government_monitors WHERE username = %s"
                monitor = execute_query(query, [username])
                if monitor and monitor[0]['password'] == password and monitor[0]['username'] == username:
                    request.session['user_id'] = monitor[0]['monitor_id']
                    request.session['role'] = role
                    return redirect('monitor_dashboard')
                else:
                    messages.error(request, 'Invalid monitor credentials')
            except Exception as e:
                messages.error(request, f'Database error: {e}')

        elif role == 'Panchayat Employee':
            # Handle Panchayat Employee login
            try:
                query = "SELECT * FROM panchayat_committee_members WHERE username = %s"
                employee = execute_query(query, [username])
                if employee and employee[0]['password'] == password and employee[0]['username'] == username:
                    request.session['user_id'] = employee[0]['member_id']
                    request.session['role'] = role
                    return redirect('employee_dashboard')
                else:
                    messages.error(request, 'Invalid employee credentials')
            except Exception as e:
                messages.error(request, f'Database error: {e}')

        elif role == 'Citizen':
            # Handle Citizen login
            try:
                query = "SELECT * FROM citizens WHERE username = %s"
                citizen = execute_query(query, [username])
                if citizen and citizen[0]['password'] == password and citizen[0]['username'] == username:
                    request.session['user_id'] = citizen[0]['citizen_id']
                    request.session['role'] = role
                    return redirect('citizen_dashboard')
                else:
                    messages.error(request, 'Invalid citizen credentials')
            except Exception as e:
                messages.error(request, f'Database error: {e}')

        else:
            messages.error(request, 'Invalid role selected.')

    return render(request, 'login.html')


def admin_dashboard(request):
    if 'user_id' in request.session and request.session['role'] == 'System Admin':
        return render(request, 'admin_dashboard.html')
    else:
        return redirect('login')


def monitor_dashboard(request):
    if 'user_id' in request.session and request.session['role'] == 'Government Monitor':
        return render(request, 'monitor_dashboard.html')
    else:
        return redirect('login')


def employee_dashboard(request):
    if 'user_id' in request.session and request.session['role'] == 'Panchayat Employee':
        return render(request, 'employee_dashboard.html')
    else:
        return redirect('login')


def citizen_dashboard(request):
    if 'user_id' in request.session and request.session['role'] == 'Citizen':
        return render(request, 'citizen_dashboard.html')
    else:
        return redirect('login')




def logout_view(request):
    # Safely remove session keys
    request.session.pop('user_id', None)  # No error if 'user_id' doesn't exist
    request.session.pop('role', None)     # No error if 'role' doesn't exist
    messages.success(request, "You have been logged out.")
    return redirect('login')


def citizen_profile(request):
    citizen_id = request.session.get('user_id')
    try:
        query = """
            SELECT c.citizen_id, c.username, c.name, c.gender, c.dob, c.contact_number, 
                   c.educational_qualification, c.household_id, h.income, h.address
            FROM citizens c
            LEFT JOIN households h ON c.household_id = h.household_id
            WHERE c.citizen_id = %s
        """
        profile = execute_query(query, [citizen_id])[0] if execute_query(query, [citizen_id]) else None
        return render(request, 'citizen_profile.html', {'profile': profile})
    except Exception as e:
        messages.error(request, f'Database error: {e}')
        return redirect('citizen_dashboard')


def citizen_vaccinations(request):
    citizen_id = request.session.get('user_id')
    try:
        query = "SELECT * FROM vaccinations WHERE citizen_id = %s"
        vaccinations = execute_query(query, [citizen_id])
        return render(request, 'citizen_vaccinations.html', {'vaccinations': vaccinations})
    except Exception as e:
        messages.error(request, f'Database error: {e}')
        return redirect('citizen_dashboard')

def citizen_schemes_enrolled(request):
    citizen_id = request.session.get('user_id')
    try:
        query = """
            SELECT ws.scheme_name, se.enrollment_date
            FROM scheme_enrollments se
            JOIN welfare_schemes ws ON se.scheme_id = ws.scheme_id
            WHERE se.citizen_id = %s
        """
        schemes = execute_query(query, [citizen_id])
        return render(request, 'citizen_schemes_enrolled.html', {'schemes': schemes})
    except Exception as e:
        messages.error(request, f'Database error: {e}')
        return redirect('citizen_dashboard')


def citizen_taxes(request):
    citizen_id = request.session.get('user_id')
    try:
        query = "SELECT * FROM citizen_taxes WHERE citizen_id = %s"
        taxes = execute_query(query, [citizen_id])
        return render(request, 'citizen_taxes.html', {'taxes': taxes})
    except Exception as e:
        messages.error(request, f'Database error: {e}')
        return redirect('citizen_dashboard')

def citizen_land_records(request):
    citizen_id = request.session.get('user_id')
    try:
        query = "SELECT * FROM land_records WHERE citizen_id = %s"
        land_records = execute_query(query, [citizen_id])
        return render(request, 'citizen_land_records.html', {'land_records': land_records})
    except Exception as e:
        messages.error(request, f'Database error: {e}')
        return redirect('citizen_dashboard')


from django.shortcuts import render, redirect
from django.contrib import messages

# Other imports...



# Manage Households
def households(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            address = request.POST.get('address')
            income = request.POST.get('income')
            try:
                query = "INSERT INTO households (address, income) VALUES (%s, %s)"
                execute_query(query, [address, income])
                messages.success(request, "Household added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding household: {e}")
        elif action == "edit":
             household_id = request.POST.get('household_id')
             address = request.POST.get('address')
             income = request.POST.get('income')
             try:
                 query = "UPDATE households SET address = %s, income = %s WHERE household_id = %s"
                 execute_query(query, [address, income, household_id])
                 messages.success(request, "Household edited successfully.")
             except Exception as e:
                 messages.error(request, f"Error editing household: {e}")
        elif action == "delete":
            household_id = request.POST.get('household_id')
            try:
                query = "DELETE FROM households WHERE household_id = %s"
                execute_query(query, [household_id])
                messages.success(request, "Household deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting household: {e}")

        return redirect('households')

    households = execute_query("SELECT * FROM households")
    return render(request, 'households.html', {'households': households})

# Manage Citizens
def citizens(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            username = request.POST.get('username')
            password = request.POST.get('password')
            name = request.POST.get('name')
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            household_id = request.POST.get('household_id')
            contact_number = request.POST.get('contact_number')
            educational_qualification = request.POST.get('educational_qualification')
            role = request.POST.get('role')
            try:
                query = "INSERT INTO citizens (username, password, name, gender, dob, household_id, contact_number, educational_qualification, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                execute_query(query, [username, password, name, gender, dob, household_id, contact_number, educational_qualification, role])
                messages.success(request, "Citizen added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding citizen: {e}")
        elif action == "edit":
            citizen_id = request.POST.get('citizen_id')
            username = request.POST.get('username')
            password = request.POST.get('password')
            name = request.POST.get('name')
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            household_id = request.POST.get('household_id')
            contact_number = request.POST.get('contact_number')
            educational_qualification = request.POST.get('educational_qualification')
            role = request.POST.get('role')
            try:
                query = "UPDATE citizens SET username = %s, password = %s, name = %s, gender = %s, dob = %s, household_id = %s, contact_number = %s, educational_qualification = %s, role = %s WHERE citizen_id = %s"
                execute_query(query, [username, password, name, gender, dob, household_id, contact_number, educational_qualification, role, citizen_id])
                messages.success(request, "Citizen edited successfully.")
            except Exception as e:
                messages.error(request, f"Error editing citizen: {e}")
        elif action == "delete":
            citizen_id = request.POST.get('citizen_id')
            try:
                query = "DELETE FROM citizens WHERE citizen_id = %s"
                execute_query(query, [citizen_id])
                messages.success(request, "Citizen deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting citizen: {e}")

        return redirect('citizens')

    citizens = execute_query("SELECT * FROM citizens")
    return render(request, 'citizens.html', {'citizens': citizens})

# Manage Land Records
def land_records(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            citizen_id = request.POST.get('citizen_id')
            area_acres = request.POST.get('area_acres')
            crop_type = request.POST.get('crop_type')
            try:
                query = "INSERT INTO land_records (citizen_id, area_acres, crop_type) VALUES (%s, %s, %s)"
                execute_query(query, [citizen_id, area_acres, crop_type])
                messages.success(request, "Land record added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding land record: {e}")
        elif action == "edit":
            land_id = request.POST.get('land_id')
            citizen_id = request.POST.get('citizen_id')
            area_acres = request.POST.get('area_acres')
            crop_type = request.POST.get('crop_type')
            try:
                query = "UPDATE land_records SET citizen_id = %s, area_acres = %s, crop_type = %s WHERE land_id = %s"
                execute_query(query, [citizen_id, area_acres, crop_type, land_id])
                messages.success(request, "Land record edited successfully.")
            except Exception as e:
                messages.error(request, f"Error editing land record: {e}")
        elif action == "delete":
            land_id = request.POST.get('land_id')
            try:
                query = "DELETE FROM land_records WHERE land_id = %s"
                execute_query(query, [land_id])
                messages.success(request, "Land record deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting land record: {e}")

        return redirect('land_records')

    land_records = execute_query("SELECT * FROM land_records")
    return render(request, 'land_records.html', {'land_records': land_records})

# Manage Welfare Schemes Enrollment
def welfare_schemes_enrollment(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            citizen_id = request.POST.get('citizen_id')
            scheme_id = request.POST.get('scheme_id')
            enrollment_date = request.POST.get('enrollment_date')
            try:
                query = "INSERT INTO scheme_enrollments (citizen_id, scheme_id, enrollment_date) VALUES (%s, %s, %s)"
                execute_query(query, [citizen_id, scheme_id, enrollment_date])
                messages.success(request, "Scheme enrollment added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding scheme enrollment: {e}")
        elif action == "edit":
            enrollment_id = request.POST.get('enrollment_id')
            citizen_id = request.POST.get('citizen_id')
            scheme_id = request.POST.get('scheme_id')
            enrollment_date = request.POST.get('enrollment_date')
            try:
                query = "UPDATE scheme_enrollments SET citizen_id = %s, scheme_id = %s, enrollment_date = %s WHERE enrollment_id = %s"
                execute_query(query, [citizen_id, scheme_id, enrollment_date, enrollment_id])
                messages.success(request, "Scheme enrollment edited successfully.")
            except Exception as e:
                messages.error(request, f"Error editing scheme enrollment: {e}")
        elif action == "delete":
            enrollment_id = request.POST.get('enrollment_id')
            try:
                query = "DELETE FROM scheme_enrollments WHERE enrollment_id = %s"
                execute_query(query, [enrollment_id])
                messages.success(request, "Scheme enrollment deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting scheme enrollment: {e}")

        return redirect('welfare_schemes_enrollment')

    enrollments = execute_query("SELECT * FROM scheme_enrollments")
    return render(request, 'welfare_schemes_enrollment.html', {'enrollments': enrollments})

# Manage Taxes
def taxes(request):  # Keep the same function name, or change it if you prefer
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            citizen_id = request.POST.get('citizen_id')
            tax_type = request.POST.get('tax_type')
            tax_amount = request.POST.get('tax_amount')
            collection_date = request.POST.get('collection_date')
            try:
                query = "INSERT INTO citizen_taxes (citizen_id, tax_type, tax_amount, collection_date) VALUES (%s, %s, %s, %s)"
                execute_query(query, [citizen_id, tax_type, tax_amount, collection_date])
                messages.success(request, "Tax record added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding tax record: {e}")
        elif action == "edit":
            tax_id = request.POST.get('tax_id')
            citizen_id = request.POST.get('citizen_id')
            tax_type = request.POST.get('tax_type')
            tax_amount = request.POST.get('tax_amount')
            collection_date = request.POST.get('collection_date')
            try:
                query = "UPDATE citizen_taxes SET citizen_id = %s, tax_type = %s, tax_amount = %s, collection_date = %s WHERE tax_id = %s"
                execute_query(query, [citizen_id, tax_type, tax_amount, collection_date, tax_id])
                messages.success(request, "Tax record edited successfully.")
            except Exception as e:
                messages.error(request, f"Error editing tax record: {e}")
        elif action == "delete":
            tax_id = request.POST.get('tax_id')
            try:
                query = "DELETE FROM citizen_taxes WHERE tax_id = %s"
                execute_query(query, [tax_id])
                messages.success(request, "Tax record deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting tax record: {e}")

        return redirect('taxes')  # Changed redirect URL

    taxes = execute_query("SELECT * FROM citizen_taxes")
    return render(request, 'taxes.html', {'taxes': taxes})  # Updated template name


# Manage Assets
def assets(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            asset_name = request.POST.get('asset_name')
            asset_type = request.POST.get('asset_type')
            installation_date = request.POST.get('installation_date')
            try:
                query = "INSERT INTO assets (asset_name, asset_type, installation_date) VALUES (%s, %s, %s)"
                execute_query(query, [asset_name, asset_type, installation_date])
                messages.success(request, "Asset added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding asset: {e}")
        elif action == "edit":
            asset_id = request.POST.get('asset_id')
            asset_name = request.POST.get('asset_name')
            asset_type = request.POST.get('asset_type')
            installation_date = request.POST.get('installation_date')
            try:
                query = "UPDATE assets SET asset_name = %s, asset_type = %s, installation_date = %s WHERE asset_id = %s"
                execute_query(query, [asset_name, asset_type, installation_date, asset_id])
                messages.success(request, "Asset edited successfully.")
            except Exception as e:
                messages.error(request, f"Error editing asset: {e}")
        elif action == "delete":
            asset_id = request.POST.get('asset_id')
            try:
                query = "DELETE FROM assets WHERE asset_id = %s"
                execute_query(query, [asset_id])
                messages.success(request, "Asset deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting asset: {e}")

        return redirect('assets')

    assets = execute_query("SELECT * FROM assets")
    return render(request, 'assets.html', {'assets': assets})

# Manage Expenditures
def expenditures(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            category = request.POST.get('category')
            amount = request.POST.get('amount')
            date_of_expenditure = request.POST.get('date_of_expenditure')
            try:
                query = "INSERT INTO expenditures (category, amount, date_of_expenditure) VALUES (%s, %s, %s)"
                execute_query(query, [category, amount, date_of_expenditure])
                messages.success(request, "Expenditure added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding expenditure: {e}")
        elif action == "edit":
            expend_id = request.POST.get('expend_id')
            category = request.POST.get('category')
            amount = request.POST.get('amount')
            date_of_expenditure = request.POST.get('date_of_expenditure')
            try:
                query = "UPDATE expenditures SET category = %s, amount = %s, date_of_expenditure = %s WHERE expend_id = %s"
                execute_query(query, [category, amount, date_of_expenditure, expend_id])
                messages.success(request, "Expenditure edited successfully.")
            except Exception as e:
                messages.error(request, f"Error editing expenditure: {e}")
        elif action == "delete":
            expend_id = request.POST.get('expend_id')
            try:
                query = "DELETE FROM expenditures WHERE expend_id = %s"
                execute_query(query, [expend_id])
                messages.success(request, "Expenditure deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting expenditure: {e}")

        return redirect('expenditures')

    expenditures = execute_query("SELECT * FROM expenditures")
    return render(request, 'expenditures.html', {'expenditures': expenditures})

# Manage Vaccinations
def vaccinations(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            citizen_id = request.POST.get('citizen_id')
            vaccine_type = request.POST.get('vaccine_type')
            date_administered = request.POST.get('date_administered')
            try:
                query = "INSERT INTO vaccinations (citizen_id, vaccine_type, date_administered) VALUES (%s, %s, %s)"
                execute_query(query, [citizen_id, vaccine_type, date_administered])
                messages.success(request, "Vaccination added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding vaccination: {e}")
        elif action == "edit":
            vaccination_id = request.POST.get('vaccination_id')
            citizen_id = request.POST.get('citizen_id')
            vaccine_type = request.POST.get('vaccine_type')
            date_administered = request.POST.get('date_administered')
            try:
                query = "UPDATE vaccinations SET citizen_id = %s, vaccine_type = %s, date_administered = %s WHERE vaccination_id = %s"
                execute_query(query, [citizen_id, vaccine_type, date_administered, vaccination_id])
                messages.success(request, "Vaccination edited successfully.")
            except Exception as e:
                messages.error(request, f"Error editing vaccination: {e}")
        elif action == "delete":
            vaccination_id = request.POST.get('vaccination_id')
            try:
                query = "DELETE FROM vaccinations WHERE vaccination_id = %s"
                execute_query(query, [vaccination_id])
                messages.success(request, "Vaccination deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting vaccination: {e}")

        return redirect('vaccinations')

    vaccinations = execute_query("SELECT * FROM vaccinations")
    return render(request, 'vaccinations.html', {'vaccinations': vaccinations})

# Manage Census Data
def census_data(request):
    # Calculate total citizens (population)
    total_citizens = execute_query("SELECT COUNT(*) AS total FROM citizens")[0]['total']
    
    # Calculate male/female population
    male_population = execute_query(
        "SELECT COUNT(*) AS total FROM citizens WHERE gender = 'Male'"
    )[0]['total']
    
    female_population = execute_query(
        "SELECT COUNT(*) AS total FROM citizens WHERE gender = 'Female'"
    )[0]['total']
    
    # Calculate total households
    total_households = execute_query("SELECT COUNT(*) AS total FROM households")[0]['total']
    
    context = {
        'total_citizens': total_citizens,
        'male_population': male_population,
        'female_population': female_population,
        'total_households': total_households,
    }
    
    return render(request, 'census_data.html', context)



# Households Statistics
def monitor_households(request):
    """
    Fetches income distribution statistics for households.
    """
    income_distribution = {
        '<= ₹30,000': execute_query("SELECT COUNT(*) AS total FROM households WHERE income <= 30000")[0]['total'],
        '₹30,001 - ₹100,000': execute_query("SELECT COUNT(*) AS total FROM households WHERE income > 30000 AND income <= 100000")[0]['total'],
        '> ₹100,000': execute_query("SELECT COUNT(*) AS total FROM households WHERE income > 100000")[0]['total'],
    }
    total_households = sum(income_distribution.values())
    return render(request, 'monitor_households.html', {
        'income_distribution': income_distribution,
        'total_households': total_households,
    })

# Citizens Statistics
def monitor_citizens(request):
    """
    Fetches gender distribution statistics for citizens.
    """
    male_count = execute_query("SELECT COUNT(*) AS total FROM citizens WHERE gender = 'Male'")[0]['total']
    female_count = execute_query("SELECT COUNT(*) AS total FROM citizens WHERE gender = 'Female'")[0]['total']
    total_citizens = male_count + female_count
    return render(request, 'monitor_citizens.html', {
        'male_count': male_count,
        'female_count': female_count,
        'total_citizens': total_citizens,
    })

# Land Records Statistics
def monitor_land_records(request):
    """
    Fetches crop type distribution statistics for land records.
    """
    crop_distribution = execute_query("""
        SELECT crop_type, SUM(area_acres) AS total_area, COUNT(*) AS record_count 
        FROM land_records 
        GROUP BY crop_type
    """)
    return render(request, 'monitor_land_records.html', {'crop_distribution': crop_distribution})

# Welfare Schemes Enrollment Statistics
def monitor_welfare_schemes_enrollment(request):
    """
    Fetches the number of beneficiaries for each welfare scheme.
    """
    schemes_distribution = execute_query("""
        SELECT ws.scheme_name AS scheme_name, COUNT(se.citizen_id) AS beneficiary_count 
        FROM scheme_enrollments se 
        JOIN welfare_schemes ws ON se.scheme_id = ws.scheme_id 
        GROUP BY ws.scheme_name
    """)
    return render(request, 'monitor_welfare_schemes_enrollment.html', {'schemes_distribution': schemes_distribution})

# Taxes Statistics
def monitor_taxes(request):
    """
    Fetches tax collection statistics by tax type.
    """
    taxes_distribution = execute_query("""
        SELECT tax_type, SUM(tax_amount) AS total_amount 
        FROM citizen_taxes 
        GROUP BY tax_type
    """)
    return render(request, 'monitor_taxes.html', {'taxes_distribution': taxes_distribution})

# Assets Statistics
def monitor_assets(request):
    """
    Fetches asset distribution statistics by asset type.
    """
    assets_distribution = execute_query("""
        SELECT asset_type, COUNT(*) AS asset_count 
        FROM assets 
        GROUP BY asset_type
    """)
    return render(request, 'monitor_assets.html', {'assets_distribution': assets_distribution})

# Expenditures Statistics
def monitor_expenditures(request):
    """
    Fetches expenditure statistics by category.
    """
    expenditures_distribution = execute_query("""
        SELECT category, SUM(amount) AS total_amount 
        FROM expenditures 
        GROUP BY category
    """)
    return render(request, 'monitor_expenditures.html', {'expenditures_distribution': expenditures_distribution})

# Vaccinations Statistics
def monitor_vaccinations(request):
    """
    Fetches vaccination statistics by vaccine type.
    """
    vaccinations_distribution = execute_query("""
        SELECT vaccine_type, COUNT(*) AS total_count 
        FROM vaccinations 
        GROUP BY vaccine_type
    """)
    return render(request, 'monitor_vaccinations.html', {'vaccinations_distribution': vaccinations_distribution})


    # Main Registration Page
def register(request):
    return render(request, 'register.html')

# # Government Monitor Registration
# def government_monitor_register(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         # Save data into the database
#         execute_query(
#             "INSERT INTO government_monitors (name, username, password) VALUES (%s, %s, %s)",
#             [name, username, password]
#         )
        
#         # Redirect to login page after successful registration
#         return redirect('login')

#     return render(request, 'government_monitor_register.html')


# Panchayat Employee Flow
def panchayat_employee_check(request):
    if request.method == 'POST':
        citizen_id = request.POST.get('citizen_id')
        result = execute_query(
            "SELECT * FROM citizens WHERE citizen_id = %s", 
            [citizen_id]
        )
        if result:
            return redirect('panchayat_employee_register', citizen_id=citizen_id)
        else:
            return redirect('citizen_register')
    return render(request, 'panchayat_employee_check.html')

# def citizen_register(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         username = request.POST.get('username')
#         password = request.POST.get('password')
        
#         execute_query(
#             "INSERT INTO citizens (name, username, password) VALUES (%s, %s, %s)",
#             [name, username, password]
#         )
#         return redirect('login')
#     return render(request, 'citizen_register.html')

# def panchayat_employee_register(request, citizen_id):
#     if request.method == 'POST':
#         department = request.POST.get('department')
#         position = request.POST.get('position')
        
#         execute_query(
#             "INSERT INTO panchayat_employees (citizen_id, department, position) VALUES (%s, %s, %s)",
#             [citizen_id, department, position]
#         )
#         return redirect('login')
#     return render(request, 'panchayat_employee_register.html', {'citizen_id': citizen_id})



from django.shortcuts import render, redirect
from django.contrib import messages


def citizen_register(request):
    """
    Handles citizen registration and saves data to the citizens table.
    If a household with the given address and income does not exist, creates a new one.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        contact_number = request.POST.get('contact_number')
        educational_qualification = request.POST.get('educational_qualification')
        address = request.POST.get('address')
        income = request.POST.get('income')
        role = request.POST.get('role')  # ✅ New Role Field

        # Check if the username already exists
        existing_user = execute_query("SELECT * FROM citizens WHERE username = %s", [username])
        if existing_user:
            return render(request, 'citizen_register.html', {
                'error': 'Username already exists. Please choose a different username.',
                'form_data': {
                    'name': name,
                    'gender': gender,
                    'dob': dob,
                    'contact_number': contact_number,
                    'educational_qualification': educational_qualification,
                    'address': address,
                    'income': income,
                    'role': role  # ✅ Preserve selected role in case of error
                }
            })

        # Check if household already exists with the given address & income
        household = execute_query("SELECT household_id FROM households WHERE address = %s AND income = %s", [address, income])

        if household:
            household_id = household[0]['household_id']  # Use existing household_id
        else:
            # Create a new household
            execute_query("INSERT INTO households (address, income) VALUES (%s, %s)", [address, income])
            new_household = execute_query("SELECT lastval() AS household_id")  # Get last inserted ID
            household_id = new_household[0]['household_id']

        # Insert the new citizen and link to household
        execute_query("""
            INSERT INTO citizens (username, password, name, gender, dob, household_id, contact_number, educational_qualification, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [username, password, name, gender, dob, household_id, contact_number, educational_qualification, role])  # ✅ Role Added

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('login')

    return render(request, 'citizen_register.html')




def panchayat_employee_check(request):
    if request.method == "POST":
        citizen_id = request.POST.get("citizen_id")

        # Check if the Citizen ID exists in the database
        citizen = execute_query("SELECT * FROM citizens WHERE citizen_id = %s", [citizen_id])

        if not citizen:
            messages.error(request, "Citizen ID not found. Please enter a valid Citizen ID.")
            return render(request, "panchayat_employee_check.html")

        # Check if the Citizen ID is already an employee in panchayat_committee_members
        employee_check = execute_query("SELECT * FROM panchayat_committee_members WHERE citizen_id = %s", [citizen_id])

        if employee_check:
            messages.error(request, "This Citizen ID is already linked to a Panchayat Employee.")
            return render(request, "panchayat_employee_check.html")

        # If valid, redirect to the Panchayat Employee Registration page
        return redirect("panchayat_employee_register", citizen_id=citizen_id)

    return render(request, "panchayat_employee_check.html")


def panchayat_employee_register(request, citizen_id):
    """
    Handles Panchayat Employee registration and saves data to the panchayat_committee_members table.
    """
    if request.method == 'POST':
        role = request.POST.get('role')
        term_start_date = request.POST.get('term_start_date')
        term_end_date = request.POST.get('term_end_date')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the username already exists
        existing_user = execute_query(
            "SELECT * FROM panchayat_committee_members WHERE username = %s", [username]
        )
        
        if existing_user:
            # Username already exists, return an error message
            return render(request, 'panchayat_employee_register.html', {
                'error': 'Username already exists. Please choose a different username.',
                'citizen_id': citizen_id,
                'role': role,
                'term_start_date': term_start_date,
                'term_end_date': term_end_date,
                'username': username,
            })

        # Validate that term start date is before term end date
        if term_start_date >= term_end_date:
            return render(request, 'panchayat_employee_register.html', {
                'error': 'Term start date must be before term end date.',
                'citizen_id': citizen_id,
                'role': role,
                'term_start_date': term_start_date,
                'term_end_date': term_end_date,
                'username': username,
            })

        # Insert into panchayat_committee_members table
        execute_query("""
            INSERT INTO panchayat_committee_members (citizen_id, role, term_start_date, term_end_date, username, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, [citizen_id, role, term_start_date, term_end_date, username, password])

        return redirect('login')

    return render(request, 'panchayat_employee_register.html', {'citizen_id': citizen_id})



def government_monitor_register(request):
    """
    Handles Government Monitor registration and ensures username uniqueness.
    Links the user to an existing household or creates a new one if necessary.
    """
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        contact_number = request.POST.get('contact_number')
        educational_qualification = request.POST.get('educational_qualification')
        username = request.POST.get('username')
        password = request.POST.get('password')
        address = request.POST.get('address')
        income = request.POST.get('income')

        # Check if the username already exists
        existing_user = execute_query(
            "SELECT * FROM government_monitors WHERE username = %s", [username]
        )
        
        if existing_user:
            # Username already exists, return an error message
            return render(request, 'government_monitor_register.html', {
                'error': 'Username already exists. Please choose a different username.',
                'form_data': {
                    'name': name,
                    'gender': gender,
                    'dob': dob,
                    'address': address,
                    'income': income,
                    'contact_number': contact_number,
                    'educational_qualification': educational_qualification,
                }
            })

        # Check if the household already exists
        household = execute_query(
            "SELECT household_id FROM households WHERE address = %s AND income = %s;",
            [address, income]
        )

        if not household:
            # Create new household
            execute_query(
                "INSERT INTO households (address, income) VALUES (%s, %s) RETURNING household_id;",
                [address, income]
            )
            household = execute_query(
                "SELECT household_id FROM households WHERE address = %s AND income = %s;",
                [address, income]
            )

        household_id = household[0]['household_id']

        # Insert into government_monitors table
        execute_query("""
            INSERT INTO government_monitors (name, gender, dob, household_id,
                                             contact_number,
                                             educational_qualification,
                                             username,
                                             password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, [name, gender, dob, household_id, contact_number,
              educational_qualification, username, password])

        # Redirect to login page after successful registration
        return redirect('login')

    return render(request, 'government_monitor_register.html')



def manage_government_monitors(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            name = request.POST.get('name')
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            contact_number = request.POST.get('contact_number')

            execute_query(
                "INSERT INTO government_monitors (name, gender, dob, contact_number) VALUES (%s, %s, %s, %s)",
                [name, gender, dob, contact_number]
            )
            messages.success(request, "Government monitor added successfully!")

        elif action == 'edit':
            monitor_id = request.POST.get('monitor_id')
            name = request.POST.get('name')
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            contact_number = request.POST.get('contact_number')

            execute_query(
                """UPDATE government_monitors 
                SET name=%s, gender=%s, dob=%s, contact_number=%s 
                WHERE monitor_id=%s""",
                [name, gender, dob, contact_number, monitor_id]
            )
            messages.success(request, "Government monitor updated successfully!")

        elif action == 'delete':
            monitor_id = request.POST.get('monitor_id')
            execute_query("DELETE FROM government_monitors WHERE monitor_id=%s", [monitor_id])
            messages.success(request, "Government monitor deleted successfully!")

    monitors = execute_query("SELECT * FROM government_monitors")
    return render(request, 'manage_government_monitors.html', {'government_monitors': monitors})

# ========================
# Panchayat Employees
# ========================
def manage_panchayat_employees(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            citizen_id = request.POST.get('citizen_id')
            role = request.POST.get('role')
            term_start = request.POST.get('term_start_date')
            term_end = request.POST.get('term_end_date')

            execute_query(
                """INSERT INTO panchayat_committee_members 
                (citizen_id, role, term_start_date, term_end_date) 
                VALUES (%s, %s, %s, %s)""",
                [citizen_id, role, term_start, term_end]
            )
            messages.success(request, "Panchayat employee added successfully!")

        elif action == 'edit':
            member_id = request.POST.get('member_id')  # Changed from employee_id
            citizen_id = request.POST.get('citizen_id')
            role = request.POST.get('role')
            term_start = request.POST.get('term_start_date')
            term_end = request.POST.get('term_end_date')

            execute_query(
                """UPDATE panchayat_committee_members 
                SET citizen_id=%s, role=%s, term_start_date=%s, term_end_date=%s 
                WHERE member_id=%s""",
                [citizen_id, role, term_start, term_end, member_id]
            )
            messages.success(request, "Panchayat employee updated successfully!")

        elif action == 'delete':
            member_id = request.POST.get('member_id')  # Changed from employee_id
            execute_query("DELETE FROM panchayat_committee_members WHERE member_id=%s", [member_id])
            messages.success(request, "Panchayat employee deleted successfully!")

    employees = execute_query("SELECT member_id, citizen_id, role, term_start_date, term_end_date FROM panchayat_committee_members")

    return render(request, 'manage_panchayat_employees.html', {'panchayat_employees': employees})



# Manage Households
def manage_households(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            address = request.POST.get('address')
            income = request.POST.get('income')
            try:
                query = "INSERT INTO households (address, income) VALUES (%s, %s)"
                execute_query(query, [address, income])
                messages.success(request, "Household added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding household: {e}")
        elif action == "edit":
             household_id = request.POST.get('household_id')
             address = request.POST.get('address')
             income = request.POST.get('income')
             try:
                 query = "UPDATE households SET address = %s, income = %s WHERE household_id = %s"
                 execute_query(query, [address, income, household_id])
                 messages.success(request, "Household edited successfully.")
             except Exception as e:
                 messages.error(request, f"Error editing household: {e}")
        elif action == "delete":
            household_id = request.POST.get('household_id')
            try:
                query = "DELETE FROM households WHERE household_id = %s"
                execute_query(query, [household_id])
                messages.success(request, "Household deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting household: {e}")

        return redirect('manage_households')

    households = execute_query("SELECT * FROM households")
    return render(request, 'manage_households.html', {'households': households})

# Manage Citizens
def manage_citizens(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            username = request.POST.get('username')
            password = request.POST.get('password')
            name = request.POST.get('name')
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            household_id = request.POST.get('household_id')
            contact_number = request.POST.get('contact_number')
            educational_qualification = request.POST.get('educational_qualification')
            role = request.POST.get('role')
            try:
                query = "INSERT INTO citizens (username, password, name, gender, dob, household_id, contact_number, educational_qualification, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                execute_query(query, [username, password, name, gender, dob, household_id, contact_number, educational_qualification, role])
                messages.success(request, "Citizen added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding citizen: {e}")
        elif action == "edit":
            citizen_id = request.POST.get('citizen_id')
            username = request.POST.get('username')
            password = request.POST.get('password')
            name = request.POST.get('name')
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            household_id = request.POST.get('household_id')
            contact_number = request.POST.get('contact_number')
            educational_qualification = request.POST.get('educational_qualification')
            role = request.POST.get('role')
            try:
                query = "UPDATE citizens SET username = %s, password = %s, name = %s, gender = %s, dob = %s, household_id = %s, contact_number = %s, educational_qualification = %s, role = %s WHERE citizen_id = %s"
                execute_query(query, [username, password, name, gender, dob, household_id, contact_number, educational_qualification, role, citizen_id])
                messages.success(request, "Citizen edited successfully.")
            except Exception as e:
                messages.error(request, f"Error editing citizen: {e}")
        elif action == "delete":
            citizen_id = request.POST.get('citizen_id')
            try:
                query = "DELETE FROM citizens WHERE citizen_id = %s"
                execute_query(query, [citizen_id])
                messages.success(request, "Citizen deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting citizen: {e}")

        return redirect('manage_citizens')

    citizens = execute_query("SELECT * FROM citizens")
    return render(request, 'manage_citizens.html', {'citizens': citizens})

# Manage Land Records
def manage_land_records(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            citizen_id = request.POST.get('citizen_id')
            area_acres = request.POST.get('area_acres')
            crop_type = request.POST.get('crop_type')
            try:
                query = "INSERT INTO land_records (citizen_id, area_acres, crop_type) VALUES (%s, %s, %s)"
                execute_query(query, [citizen_id, area_acres, crop_type])
                messages.success(request, "Land record added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding land record: {e}")
        elif action == "edit":
            land_id = request.POST.get('land_id')
            citizen_id = request.POST.get('citizen_id')
            area_acres = request.POST.get('area_acres')
            crop_type = request.POST.get('crop_type')
            try:
                query = "UPDATE land_records SET citizen_id = %s, area_acres = %s, crop_type = %s WHERE land_id = %s"
                execute_query(query, [citizen_id, area_acres, crop_type, land_id])
                messages.success(request, "Land record edited successfully.")
            except Exception as e:
                messages.error(request, f"Error editing land record: {e}")
        elif action == "delete":
            land_id = request.POST.get('land_id')
            try:
                query = "DELETE FROM land_records WHERE land_id = %s"
                execute_query(query, [land_id])
                messages.success(request, "Land record deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting land record: {e}")

        return redirect('manage_land_records')

    land_records = execute_query("SELECT * FROM land_records")
    return render(request, 'manage_land_records.html', {'land_records': land_records})

# Manage Welfare Schemes Enrollment
def manage_welfare_schemes_enrollment(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            citizen_id = request.POST.get('citizen_id')
            scheme_id = request.POST.get('scheme_id')
            enrollment_date = request.POST.get('enrollment_date')
            try:
                query = "INSERT INTO scheme_enrollments (citizen_id, scheme_id, enrollment_date) VALUES (%s, %s, %s)"
                execute_query(query, [citizen_id, scheme_id, enrollment_date])
                messages.success(request, "Scheme enrollment added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding scheme enrollment: {e}")
        elif action == "edit":
            enrollment_id = request.POST.get('enrollment_id')
            citizen_id = request.POST.get('citizen_id')
            scheme_id = request.POST.get('scheme_id')
            enrollment_date = request.POST.get('enrollment_date')
            try:
                query = "UPDATE scheme_enrollments SET citizen_id = %s, scheme_id = %s, enrollment_date = %s WHERE enrollment_id = %s"
                execute_query(query, [citizen_id, scheme_id, enrollment_date, enrollment_id])
                messages.success(request, "Scheme enrollment edited successfully.")
            except Exception as e:
                messages.error(request, f"Error editing scheme enrollment: {e}")
        elif action == "delete":
            enrollment_id = request.POST.get('enrollment_id')
            try:
                query = "DELETE FROM scheme_enrollments WHERE enrollment_id = %s"
                execute_query(query, [enrollment_id])
                messages.success(request, "Scheme enrollment deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting scheme enrollment: {e}")

        return redirect('manage_welfare_schemes_enrollment')

    enrollments = execute_query("SELECT * FROM scheme_enrollments")
    return render(request, 'manage_welfare_schemes_enrollment.html', {'enrollments': enrollments})

# Manage Taxes
def manage_taxes(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            citizen_id = request.POST.get('citizen_id')
            tax_type = request.POST.get('tax_type')
            tax_amount = request.POST.get('tax_amount')
            collection_date = request.POST.get('collection_date')
            try:
                query = "INSERT INTO citizen_taxes (citizen_id, tax_type, tax_amount, collection_date) VALUES (%s, %s, %s, %s)"
                execute_query(query, [citizen_id, tax_type, tax_amount, collection_date])
                messages.success(request, "Tax record added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding tax record: {e}")
        elif action == "edit":
            tax_id = request.POST.get('tax_id')
            citizen_id = request.POST.get('citizen_id')
            tax_type = request.POST.get('tax_type')
            tax_amount = request.POST.get('tax_amount')
            collection_date = request.POST.get('collection_date')
            try:
                query = "UPDATE citizen_taxes SET citizen_id = %s, tax_type = %s, tax_amount = %s, collection_date = %s WHERE tax_id = %s"
                execute_query(query, [citizen_id, tax_type, tax_amount, collection_date, tax_id])
                messages.success(request, "Tax record edited successfully.")
            except Exception as e:
                messages.error(request, f"Error editing tax record: {e}")
        elif action == "delete":
            tax_id = request.POST.get('tax_id')
            try:
                query = "DELETE FROM citizen_taxes WHERE tax_id = %s"
                execute_query(query, [tax_id])
                messages.success(request, "Tax record deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting tax record: {e}")

        return redirect('manage_taxes')

    taxes = execute_query("SELECT * FROM citizen_taxes")
    return render(request, 'manage_taxes.html', {'taxes': taxes})

# Manage Assets
def manage_assets(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            asset_name = request.POST.get('asset_name')
            asset_type = request.POST.get('asset_type')
            installation_date = request.POST.get('installation_date')
            try:
                query = "INSERT INTO assets (asset_name, asset_type, installation_date) VALUES (%s, %s, %s)"
                execute_query(query, [asset_name, asset_type, installation_date])
                messages.success(request, "Asset added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding asset: {e}")
        elif action == "edit":
            asset_id = request.POST.get('asset_id')
            asset_name = request.POST.get('asset_name')
            asset_type = request.POST.get('asset_type')
            installation_date = request.POST.get('installation_date')
            try:
                query = "UPDATE assets SET asset_name = %s, asset_type = %s, installation_date = %s WHERE asset_id = %s"
                execute_query(query, [asset_name, asset_type, installation_date, asset_id])
                messages.success(request, "Asset edited successfully.")
            except Exception as e:
                messages.error(request, f"Error editing asset: {e}")
        elif action == "delete":
            asset_id = request.POST.get('asset_id')
            try:
                query = "DELETE FROM assets WHERE asset_id = %s"
                execute_query(query, [asset_id])
                messages.success(request, "Asset deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting asset: {e}")

        return redirect('manage_assets')

    assets = execute_query("SELECT * FROM assets")
    return render(request, 'manage_assets.html', {'assets': assets})

# Manage Expenditures
def manage_expenditures(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            category = request.POST.get('category')
            amount = request.POST.get('amount')
            date_of_expenditure = request.POST.get('date_of_expenditure')
            try:
                query = "INSERT INTO expenditures (category, amount, date_of_expenditure) VALUES (%s, %s, %s)"
                execute_query(query, [category, amount, date_of_expenditure])
                messages.success(request, "Expenditure added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding expenditure: {e}")
        elif action == "edit":
            expend_id = request.POST.get('expend_id')
            category = request.POST.get('category')
            amount = request.POST.get('amount')
            date_of_expenditure = request.POST.get('date_of_expenditure')
            try:
                query = "UPDATE expenditures SET category = %s, amount = %s, date_of_expenditure = %s WHERE expend_id = %s"
                execute_query(query, [category, amount, date_of_expenditure, expend_id])
                messages.success(request, "Expenditure edited successfully.")
            except Exception as e:
                messages.error(request, f"Error editing expenditure: {e}")
        elif action == "delete":
            expend_id = request.POST.get('expend_id')
            try:
                query = "DELETE FROM expenditures WHERE expend_id = %s"
                execute_query(query, [expend_id])
                messages.success(request, "Expenditure deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting expenditure: {e}")

        return redirect('manage_expenditures')

    expenditures = execute_query("SELECT * FROM expenditures")
    return render(request, 'manage_expenditures.html', {'expenditures': expenditures})

# Manage Vaccinations
def manage_vaccinations(request):
    if request.method == "POST":
        action = request.POST.get('action')

        if action == "add":
            citizen_id = request.POST.get('citizen_id')
            vaccine_type = request.POST.get('vaccine_type')
            date_administered = request.POST.get('date_administered')
            try:
                query = "INSERT INTO vaccinations (citizen_id, vaccine_type, date_administered) VALUES (%s, %s, %s)"
                execute_query(query, [citizen_id, vaccine_type, date_administered])
                messages.success(request, "Vaccination added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding vaccination: {e}")
        elif action == "edit":
            vaccination_id = request.POST.get('vaccination_id')
            citizen_id = request.POST.get('citizen_id')
            vaccine_type = request.POST.get('vaccine_type')
            date_administered = request.POST.get('date_administered')
            try:
                query = "UPDATE vaccinations SET citizen_id = %s, vaccine_type = %s, date_administered = %s WHERE vaccination_id = %s"
                execute_query(query, [citizen_id, vaccine_type, date_administered, vaccination_id])
                messages.success(request, "Vaccination edited successfully.")
            except Exception as e:
                messages.error(request, f"Error editing vaccination: {e}")
        elif action == "delete":
            vaccination_id = request.POST.get('vaccination_id')
            try:
                query = "DELETE FROM vaccinations WHERE vaccination_id = %s"
                execute_query(query, [vaccination_id])
                messages.success(request, "Vaccination deleted successfully.")
            except Exception as e:
                messages.error(request, f"Error deleting vaccination: {e}")

        return redirect('manage_vaccinations')

    vaccinations = execute_query("SELECT * FROM vaccinations")
    return render(request, 'manage_vaccinations.html', {'vaccinations': vaccinations})    

def manage_welfare_schemes(request):
    """
    View to manage welfare schemes - Add, Edit, Delete.
    """
    if request.method == 'POST':
        # Get form data
        scheme_id = request.POST.get('scheme_id')  # If empty, it's a new scheme
        scheme_name = request.POST.get('scheme_name')
        beneficiaries = request.POST.get('beneficiaries')
        budget = request.POST.get('budget')

        if not scheme_name or not beneficiaries or not budget:
            return render(request, 'welfare_schemes.html', {
                'schemes': execute_query("SELECT * FROM welfare_schemes"),
                'error': 'All fields are required!',
            })

        try:
            budget = float(budget)  # Ensure budget is a valid number
        except ValueError:
            return render(request, 'welfare_schemes.html', {
                'schemes': execute_query("SELECT * FROM welfare_schemes"),
                'error': 'Invalid budget amount!',
            })

        if scheme_id:  # ✅ Update existing scheme
            execute_query(
                "UPDATE welfare_schemes SET scheme_name=%s, beneficiaries=%s, budget=%s WHERE scheme_id=%s",
                [scheme_name, beneficiaries, budget, scheme_id]
            )
        else:  # ✅ Insert new scheme
            execute_query(
                "INSERT INTO welfare_schemes (scheme_name, beneficiaries, budget) VALUES (%s, %s, %s)",
                [scheme_name, beneficiaries, budget]
            )

        return redirect('manage_welfare_schemes')  # Refresh the page after adding/editing

    # ✅ Fetch all welfare schemes
    schemes = execute_query("SELECT * FROM welfare_schemes")

    return render(request, 'manage_welfare_schemes.html', {'schemes': schemes})






def delete_welfare_scheme(request, scheme_id):
    """
    Handles deletion of a welfare scheme.
    """
    execute_query("DELETE FROM welfare_schemes WHERE scheme_id = %s", [scheme_id])
    return redirect('manage_welfare_schemes')    
