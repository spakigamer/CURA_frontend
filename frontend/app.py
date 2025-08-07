# app.py
import streamlit as st
import requests

# --- PAGE CONFIG (MUST BE THE FIRST STREAMLIT COMMAND) ---
st.set_page_config(
    page_title="CURA Health Agents",
    page_icon="💊",
    layout="wide"
)

# --- PWA SETTINGS (Updated with corrected paths for Streamlit Cloud) ---
# This injects the necessary HTML to make the app a PWA
PWA_HTML = """
    <link rel="manifest" href="/app/static/manifest.json">
    <meta name="theme-color" content="#4A90E2">
    <script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('/app/static/service-worker.js').then(function(registration) {
                    console.log('ServiceWorker registration successful with scope: ', registration.scope);
                }, function(err) {
                    console.log('ServiceWorker registration failed: ', err);
                });
            });
        }
    </script>
"""
st.markdown(PWA_HTML, unsafe_allow_html=True)


# --- STATE MANAGEMENT & API SETUP ---
BASE_URL = "https://cura-backend-main-99c8.onrender.com/api"

# Initialize session state variables
if 'sessionid' not in st.session_state:
    st.session_state['sessionid'] = None
if 'page' not in st.session_state:
    st.session_state['page'] = 'Home'
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'username' not in st.session_state:
    st.session_state['username'] = 'User'

# --- UTILITY FUNCTIONS ---
def get_auth_headers():
    if st.session_state.get('sessionid'):
        return {'Cookie': f"sessionid={st.session_state['sessionid']}"}
    return {}

def set_page(page_name):
    if st.session_state['page'] != page_name:
        st.session_state['history'].append(st.session_state['page'])
    st.session_state['page'] = page_name
    st.rerun()

def go_back():
    if st.session_state['history']:
        st.session_state['page'] = st.session_state['history'].pop()
        st.rerun()

# --- HEADER & GLOBAL NAVIGATION (Updated for Vertical Layout) ---
# The elements are now stacked vertically instead of in columns.

# Show back button on all pages except Home
if st.session_state['page'] != 'Home' and st.session_state['history']:
    if st.button("⬅️ Back"):
        go_back()

st.title("CURA Health Agents")

# Show Welcome/Logout button if logged in
if st.session_state.get('sessionid'):
    st.write(f"Welcome, **{st.session_state.username}**!")
    if st.button("Log Out"):
        st.session_state['sessionid'] = None
        st.session_state['username'] = None
        st.session_state['history'] = []
        set_page('Home')

st.divider()


# --- PAGE RENDERING LOGIC ---

# --- Home Page (Updated UI) ---
if st.session_state['page'] == "Home":
    
    # --- LOGGED-IN VIEW (DASHBOARD) ---
    if st.session_state.get('sessionid'):
        st.header(f"Welcome to your Dashboard, {st.session_state.username}!")
        st.markdown("Select a health agent below to manage your health.")

        card1, card2 = st.columns(2)

        with card1:
            with st.container(border=True):
                st.subheader("💊 Medication Reminders")
                st.markdown("Manage your medication schedule, track your inventory, and set smart reminders.")
                if st.button("Go to Reminders", use_container_width=True, type="primary"):
                    set_page('Reminders')

        with card2:
            with st.container(border=True):
                st.subheader("🥗 Personalized Diet Plan")
                st.markdown("Get a daily, AI-generated diet plan tailored to your health profile and goals.")
                if st.button("Go to Diet Plan", use_container_width=True, type="primary"):
                    headers = get_auth_headers()
                    try:
                        profile_response = requests.get(f"{BASE_URL}/diet/profile/", headers=headers)
                        if profile_response.status_code == 404:
                            st.info("Let's set up your health profile first!")
                            set_page('Profile')
                        elif profile_response.status_code == 200:
                            set_page('Diet Plan')
                        else:
                            st.error("Could not verify your profile.")
                    except requests.exceptions.RequestException:
                        st.error("Could not connect to the API.")

    # --- LOGGED-OUT VIEW (LANDING PAGE) ---
    else:
        st.header("Your Personal Health Companion")
        st.markdown("#### Manage your medications and get personalized diet plans all in one place.")
        
        st.divider()
        
        # --- Key Features Section ---
        st.header("Key Features")
        feat1, feat2 = st.columns(2)
        with feat1:
            with st.container(border=True):
                st.subheader("💊 Smart Medication Reminders")
                st.markdown("- Add your medicines and dosage.")
                st.markdown("- Track your current inventory.")
                st.markdown("- Set custom reminders for each medicine.")
                st.markdown("- Mark doses as taken to automatically update inventory.")
        with feat2:
            with st.container(border=True):
                st.subheader("🥗 AI-Powered Diet Plans")
                st.markdown("- Create a detailed health profile.")
                st.markdown("- Specify dietary needs, allergies, and goals.")
                st.markdown("- Generate a full day's meal plan with one click.")
                st.markdown("- Includes recipes, calories, and a grocery list.")

        st.divider()

        # --- How It Works Section ---
        st.header("How It Works")
        step1, step2, step3 = st.columns(3)
        with step1:
            st.subheader("1. Sign Up")
            st.markdown("Create your free and secure account in seconds.")
        with step2:
            st.subheader("2. Create Profile")
            st.markdown("Fill out your health profile so our AI can understand your unique needs.")
        with step3:
            st.subheader("3. Get Plan")
            st.markdown("Access your personalized medication and diet dashboards.")
            
        st.divider()
        
        # --- Call to Action ---
        _, center_col, _ = st.columns([1, 2, 1])
        with center_col:
            st.subheader("Ready to Take Control of Your Health?")
            if st.button("Log In to Your Account", use_container_width=True, type="primary"):
                set_page('Login')
            if st.button("Create a New Account", use_container_width=True):
                set_page('Sign Up')


# --- Login / Sign Up / Profile Pages (Centered Forms) ---
def render_centered_form(page_type):
    st.header(f"{page_type}")
    _, center_col, _ = st.columns([1, 1.5, 1])
    with center_col:
        with st.container(border=True):
            if page_type == 'Log In':
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                if st.button("Log In", use_container_width=True, type="primary"):
                    try:
                        response = requests.post(f"{BASE_URL}/auth/login/", json={"email": email, "password": password})
                        if response.status_code == 200:
                            st.session_state['sessionid'] = response.cookies.get('sessionid')
                            login_data = response.json()
                            message = login_data.get('message', '')
                            try:
                                username = message.split(', ')[1].split('!')[0]
                            except IndexError:
                                username = login_data.get('email', 'User')
                            st.session_state['username'] = username
                            st.success("Logged in successfully!")
                            set_page('Home')
                        else:
                            st.error("Invalid credentials.")
                    except requests.exceptions.RequestException:
                        st.error("Could not connect to the API.")
                st.divider()
                st.markdown("Need an account?")
                if st.button("Go to Sign Up", use_container_width=True):
                    set_page('Sign Up')

            elif page_type == 'Sign Up':
                username = st.text_input("Username", key="signup_username")
                email = st.text_input("Email", key="signup_email")
                password = st.text_input("Password", type="password", key="signup_password")
                if st.button("Create Account", use_container_width=True, type="primary"):
                    signup_data = {"username": username, "email": email, "password": password}
                    try:
                        response = requests.post(f"{BASE_URL}/auth/signup/", json=signup_data)
                        if response.status_code == 201:
                            st.success("User created successfully. Please log in.")
                            set_page('Login')
                        else:
                            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                    except requests.exceptions.RequestException:
                        st.error("Could not connect to the API.")
                st.divider()
                st.markdown("Already have an account?")
                if st.button("Go to Log In", use_container_width=True):
                    set_page('Login')

            elif page_type == 'Health Profile':
                headers = get_auth_headers()
                try:
                    response = requests.get(f"{BASE_URL}/diet/profile/", headers=headers)
                    profile_data = {}
                    if response.status_code == 200:
                        profile_data = response.json()
                    
                    with st.form("profile_form"):
                        st.subheader("Your Details")
                        age = st.number_input("Age", min_value=1, value=profile_data.get('age', 25))
                        weight_kg = st.number_input("Weight (kg)", min_value=1.0, value=profile_data.get('weight_kg', 70.0), format="%.1f")
                        height_cm = st.number_input("Height (cm)", min_value=1.0, value=profile_data.get('height_cm', 175.0), format="%.1f")
                        
                        st.subheader("Lifestyle")
                        activity_level_options = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"]
                        current_activity = profile_data.get('activity_level', 'Moderately Active')
                        activity_index = activity_level_options.index(current_activity) if current_activity in activity_level_options else 2
                        activity_level = st.selectbox("Activity Level", activity_level_options, index=activity_index)

                        dietary_preferences_options = ["Non-Veg", "Vegetarian", "Vegan", "Pescatarian"]
                        current_diet = profile_data.get('dietary_preferences', 'Non-Veg')
                        diet_index = dietary_preferences_options.index(current_diet) if current_diet in dietary_preferences_options else 0
                        dietary_preferences = st.selectbox("Dietary Preferences", dietary_preferences_options, index=diet_index)

                        st.subheader("Health Information")
                        allergies = st.text_area("Allergies (comma-separated)", value=profile_data.get('allergies', ''))
                        health_issues = st.text_area("Health Issues or Goals", value=profile_data.get('health_issues', ''))
                        
                        if st.form_submit_button("Save Profile", use_container_width=True, type="primary"):
                            payload = {"age": age, "weight_kg": weight_kg, "height_cm": height_cm, "activity_level": activity_level, 
                                       "dietary_preferences": dietary_preferences, "allergies": allergies, "health_issues": health_issues}
                            response = requests.post(f"{BASE_URL}/diet/profile/", json=payload, headers=headers)
                            if response.status_code in [200, 201]:
                                st.success("Profile saved successfully!")
                                set_page('Diet Plan')
                            else:
                                st.error(f"Failed to save profile: {response.json().get('error', 'Unknown error')}")
                except requests.exceptions.RequestException:
                    st.error("Could not connect to the API.")


if st.session_state['page'] == "Login":
    render_centered_form('Log In')
elif st.session_state['page'] == "Sign Up":
    render_centered_form('Sign Up')
elif st.session_state['page'] == "Profile":
    render_centered_form('Health Profile')

# --- Reminders Page ---
elif st.session_state['page'] == "Reminders":
    st.header("💊 Medication Reminders")
    headers = get_auth_headers()
    
    with st.expander("➕ Add New Medicine"):
        with st.form("add_medicine_form"):
            med_name = st.text_input("Medicine Name")
            med_dosage = st.text_input("Dosage (e.g., 500mg)")
            med_inventory = st.number_input("Initial Inventory", min_value=0, value=0)
            if st.form_submit_button("Add Medicine", type="primary"):
                med_data = {"name": med_name, "dosage": med_dosage, "inventory": med_inventory}
                response = requests.post(f"{BASE_URL}/reminder/medicines/", json=med_data, headers=headers)
                if response.status_code == 201:
                    st.success("Medicine added!")
                    st.rerun()
                else:
                    st.error(f"Error: {response.json().get('error', 'Could not add medicine.')}")

    st.divider()
    st.subheader("Your Medicines")
    
    try:
        response = requests.get(f"{BASE_URL}/reminder/medicines/", headers=headers)
        if response.status_code == 200:
            medicines = response.json()
            if not medicines:
                st.info("You haven't added any medicines yet.")
            
            for med in medicines:
                med_id = med.get('id')
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 2, 2])
                    with c1:
                        st.subheader(f"{med.get('name', 'N/A')} - {med.get('dosage', 'N/A')}")
                    with c2:
                        st.metric("Inventory", f"{med.get('inventory', 0)} units")
                    with c3:
                        st.write("") 
                        if st.button("Delete Medicine", key=f"del_med_{med_id}", use_container_width=True):
                            requests.delete(f"{BASE_URL}/reminder/medicines/{med_id}/", headers=headers)
                            st.rerun()
                    
                    st.markdown("##### ⏰ Reminders")
                    reminders = med.get('reminders', [])
                    if not reminders:
                        st.caption("No reminders set for this medicine.")
                    for rem in reminders:
                        rem_id = rem.get('id')
                        rc1, rc2 = st.columns([4, 2])
                        with rc1:
                            st.markdown(f"**{rem.get('time', 'N/A')}:** Take {rem.get('quantity', 0)} unit(s) - *{rem.get('instruction', 'N/A')}*")
                        with rc2:
                            if st.button("Mark as Taken", key=f"take_{rem_id}", use_container_width=True):
                                requests.post(f"{BASE_URL}/reminder/reminders/{rem_id}/take/", headers=headers)
                                st.rerun()
                    
                    with st.expander("Add New Reminder"):
                        with st.form(f"add_rem_{med_id}"):
                            new_time = st.text_input("Time (HH:MM)")
                            new_qty = st.number_input("Quantity", 1, 10, 1)
                            new_inst = st.selectbox("Instruction", ["After Food", "Before Food", "With Food", "Any Time"])
                            if st.form_submit_button("Set Reminder"):
                                rem_data = {"time": new_time, "quantity": new_qty, "instruction": new_inst}
                                requests.post(f"{BASE_URL}/reminder/medicines/{med_id}/reminders/", json=rem_data, headers=headers)
                                st.rerun()
    except requests.exceptions.RequestException:
        st.error("Could not connect to the API.")

# --- Diet Plan Page ---
elif st.session_state['page'] == "Diet Plan":
    st.header("🥗 Personalized Diet Plan")
    headers = get_auth_headers()
    
    try:
        plan_response = requests.get(f"{BASE_URL}/diet/plan/", headers=headers)
        
        if plan_response.status_code == 404:
            st.info("You don't have a diet plan yet. Let's generate one!")
            if st.button("Generate My First Diet Plan", type="primary", use_container_width=True):
                with st.spinner("Creating your personalized plan..."):
                    requests.post(f"{BASE_URL}/diet/plan/generate/", headers=headers)
                    st.rerun()
        
        elif plan_response.status_code == 200:
            plan = plan_response.json()
            macros = plan.get('macronutrients', {})

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Calories", plan.get('daily_calories', 'N/A'))
            m2.metric("Protein", f"{macros.get('protein_grams', 'N/A')}g")
            m3.metric("Carbs", f"{macros.get('carbs_grams', 'N/A')}g")
            m4.metric("Fat", f"{macros.get('fat_grams', 'N/A')}g")

            st.info(f"**💡 Note from CURA:** {plan.get('notes', 'Enjoy your healthy meals!')}")
            st.divider()

            col1, col2 = st.columns([3, 2])
            with col1:
                st.subheader("🍽️ Your Meals for the Day")
                meals = plan.get('meals', {})
                for meal_name, details in meals.items():
                    with st.container(border=True):
                        st.subheader(f"{meal_name.capitalize()}: {details.get('name', 'N/A')}")
                        c1, c2 = st.columns(2)
                        c1.caption(f"🕒 Suggested Time: {details.get('time', 'N/A')}")
                        c2.caption(f"🔥 Calories: ~{details.get('calories', 'N/A')}")
                        if details.get('notes'):
                            st.write(f"*{details.get('notes')}*")

            with col2:
                st.subheader("🛒 Grocery List")
                with st.container(border=True):
                    grocery_list = plan.get('grocery_list', [])
                    for item in grocery_list:
                        st.markdown(f"- {item}")
                
                st.subheader("Actions")
                if st.button("Generate a New Plan", use_container_width=True):
                    with st.spinner("Working on a new plan..."):
                        requests.post(f"{BASE_URL}/diet/plan/generate/", headers=headers)
                        st.rerun()
                if st.button("Update Health Profile", use_container_width=True):
                    set_page('Profile')
                    
    except requests.exceptions.RequestException:
        st.error("Could not connect to the API.")
