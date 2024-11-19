from flask import *
from functions import *
import math
from functools import wraps
import os
from werkzeug.utils import secure_filename

# imports for image upload
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
app.secret_key = "jhvahsfgjsgosh.jfa/plj"


# meant for profile picture upload 
UPLOAD_FOLDER = 'static/candidate_profile_pics/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'hustle_db'
}

# def login_required(f):
#     @wraps(f)
#     # return session
#     def decorated_function(*args, **kwargs):
#         # if 'candidate_key' not in session:
#         #     flash('Kindly login to access this page.', 'danger')
#         #     return redirect(url_for('choose'))
#         # elif 'company_key' not in session:
#         #     flash('Kindly login to access this page.', 'danger')
#         #     return redirect(url_for('choose'))  
#         # else:            
#         #     return f(*args, **kwargs)
#         # try:
#             if not(session['key']):
#                 flash("Login to access the dashboard")
#                 return redirect(url_for('choose'))
#             else:            
#                 return f(*args, **kwargs)
#         # except:
#         #         flash("Login to access the dashboard")
#         #         return redirect(url_for('choose'))
#     return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'key' not in session:
            flash("Login to access the dashboard", 'danger')
            return redirect(url_for('choose'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    locations = get_locations()
    jobType = get_jobType()
    salaryRange = get_salaryRange()
    candidates = get_candidates()
    developertags = developer_tags()
    categories = category_tags()
    companies, total_records = get_companies(page=1, per_page=5)  # Initial load, first 5 companies
    total_pages = (total_records + 4) // 5  # Calculate total pages (5 items per page)
    featured_jobs = get_featured_jobs()
    return render_template('home.html', locations=locations, jobtypes=jobType, salaryranges=salaryRange, categories=categories, companies=companies, total_pages=total_pages, postedjobs = featured_jobs, candidates=candidates)
# @app.route('/candidate/dashboard')
# def candidate_dashboard():
#     return render_template('candidate/dashboard.html')

@app.route('/search', methods=['POST'])
def search():
    job_title = request.form.get('job_title')
    location = request.form.get('location')
    job_type = request.form.get('job_type')
    salary_range = request.form.get('search_salary')
    page = int(request.form.get('currentPage', 1))
    tag = request.form.get('tag')
    if tag == "None" or tag == "":
        tag = None
    if location == "None" or location == "Select Location":
        location = None
    if job_type == "None" or location == "Job Type":
        job_type = None
    
    featured_jobs = get_featured_jobs(job_title=job_title, location=location, job_type=job_type, salary_range=salary_range, tag=tag)
    per_page = 4
    pages = math.ceil(len(featured_jobs) / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = featured_jobs[start:end]
    return jsonify({'htmlresponse': render_template('components/response.html', postedjobs=paginated_data, page = page, per_page =per_page, total = pages  )})

@app.route('/cand_search_jobs', methods=['POST'])
def cand_search_jobs():
    job_title = request.form.get('job_title')
    location = request.form.get('location')
    job_type = request.form.get('job_type')
    salary_range = request.form.get('search_salary')
    page = int(request.form.get('currentPage', 1))
    tag = request.form.get('tag')
    if tag == "None" or tag == "":
        tag = None
    if location == "None" or location == "Select Location":
        location = None
    if job_type == "None" or location == "Job Type":
        job_type = None
    
    featured_jobs = get_featured_jobs(job_title=job_title, location=location, job_type=job_type, salary_range=salary_range, tag=tag)
    per_page = 12
    pages = math.ceil(len(featured_jobs) / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = featured_jobs[start:end]
    return jsonify({'htmlresponse': render_template('candidate/components/cand_dash_jobs.html', postedjobs=paginated_data, page = page, per_page =per_page, total = pages  )})


@app.route('/find-jobs')
def findJobs():
    locations = get_locations()
    categories=category_tags()
    jobType = get_jobType()
    salaryRange = get_salaryRange()
    mycompanies = get_allcompanies()
    companies, total_records = get_companies(page=1, per_page=5)  # Initial load, first 5 companies
    total_pages = (total_records + 4) // 5  # Calculate total pages (5 items per page)
    featured_jobs = get_featured_jobs()
    return render_template('find-jobs.html', categories=categories,locations=locations, jobtypes=jobType, salaryranges=salaryRange, companies=companies, total_pages=total_pages, postedjobs = featured_jobs, mycompanies=mycompanies)




@app.route('/find-talent')
def findTalent():
    candidates = get_talents()
    locations = candidates_locations()
    developertags = developer_tags()
    developertags = developer_tags()

    return render_template('find-talent.html',candidates=candidates,locations=locations,developertags=developertags)

@app.route('/choose')
def choose():
    return render_template('choose.html')

@app.route('/candidate/register', methods = ['POST', 'GET'])
def candidateReg():
    if request.method == 'POST':
        email = request.form['email']
        firstname = request.form['fname']
        surname = request.form['surname']
        password = request.form['password']
        confirm = request.form['password_confirmation']

        connection = pymysql.connect(host='localhost', user='root',password='', database='hustle_db' )
        cursor = connection.cursor()

        data = (email, firstname, surname, hash_password(password))
        sql = ''' insert into candidates (email, fname, surname, password) values (%s, %s, %s, %s) '''

        if len(email) <= 0:
            return render_template('candidate/register.html', error1 = 'Email Cannot be Empty')
        
        elif len(firstname) <= 0:
            return render_template('candidate/register.html', error2 = 'First Name Cannot be Empty')
        
        elif len(surname) <= 0:
            return render_template('candidate/register.html', error3 = 'Surname Cannot be Empty')
        
        elif len(password) <= 0:
            return render_template('candidate/register.html', error4 = 'Password Cannot be Empty')
        
        elif len(password) < 8:
            return render_template('candidate/register.html', error5 = 'Password Less Than 8 Characters')
        
        elif password != confirm:
            return render_template('candidate/register.html', error6 = 'Password Not Matching')
        
        else:
            try:
                cursor.execute(sql, data)
                connection.commit()
                return render_template('candidate/register.html', success = 'Candidate Registered')
            except:
                connection.rollback()
                return render_template('candidate/register.html', warning = 'Something Went Wrong')
    else:
        return render_template('candidate/register.html', message = "Sign-up Below")


@app.route('/candidate/login', methods = ['POST', 'GET'])
def candidateLogin():
    if request.method == 'POST':
        candidate_email = request.form['email']
        candidate_password = request.form['password']

        sql = 'select * from candidates where email = %s'

        connection = pymysql.connect(host='localhost', user='root',password='', database='hustle_db' )
        cursor = connection.cursor()
        cursor.execute(sql, candidate_email)

        count = cursor.rowcount
        if count == 0:
            return render_template('candidate/login.html', error = 'Candidate Email not Found')
        else:
            candidate = cursor.fetchone()
            hashed_password = candidate[6]
            if hash_verify(candidate_password, hashed_password):
                session['candidate_key'] = candidate[0]
                session['email'] = candidate[1]
                session['fname'] = candidate[2]
                session['surname'] = candidate[4]
                session['candidate_profile_pic'] = candidate[8]
                session['key'] = "candidate"

                return redirect('/candidate/dashboard')
            
            else:
                return render_template('candidate/login.html', error = 'Incorrect Login Credentilals')
    else:
        return render_template('candidate/login.html', message = 'Login Below')


@app.route('/search_talent', methods=['POST'])
def search_talent():

    if request.form.get('job_title') != "None":

        job_title = request.form.get('job_title')
    else:
        job_title=None
    location = request.form.get('location')
    tag = request.form.get('tag')
    page = int(request.form.get('currentPage', 1))
    if tag == "None" or tag == "":
        tag = None
    rating = request.form.get('rating')
    if rating == "None" or rating == "" or not(rating):
        rating = None
    # else: 
    #     rating = float(rating)
    if location == "None" or location == "Select Location":
        location = None
    
    candidates = get_talents(job_title=job_title, location=location, tag=tag, rating=rating)
    per_page = 24
    pages = math.ceil(len(candidates) / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = candidates[start:end]
    
    return jsonify({'htmlresponse': render_template('components/devs_response.html', candidates=paginated_data, page = page, per_page =per_page, total = pages  )})

@app.route('/company/register',  methods = ['POST', 'GET'])
def companyReg():
    if request.method == 'POST':
        company_email = request.form['company_email']
        company_name = request.form['company_name']
        password = request.form['password']
        confirm = request.form['password_confirmation']

        connection = pymysql.connect(host='localhost', user='root',password='', database='hustle_db' )
        cursor = connection.cursor()

        data = (company_name,company_email,hash_password(password))

        sql = ''' insert into companies (company_name, company_email, password) values (%s, %s, %s) '''

        if len(company_email) <= 0:
            return render_template('company/register.html', error1 = 'Email Cannot be Empty')
        
        elif len(company_name) <= 0:
            return render_template('company/register.html', error2 = 'Company Name Cannot be Empty')    

        elif len(password) <= 0:
            return render_template('company/register.html', error3 = 'Password Cannot be Empty')
        
        elif len(password) < 8:
            return render_template('company/register.html', error4 = 'Password Less Than 8 Characters')
        
        elif password != confirm:
            return render_template('company/register.html', error5 = 'Password Not Matching')
        
        else:
            try:
                cursor.execute(sql, data)
                connection.commit()
                return render_template('company/register.html', success = 'Company Registered')
            except:
                connection.rollback()
                return render_template('company/register.html', warning = 'Something Went Wrong')

    else:
        return render_template('company/register.html', message = "Register Your Company Below")
    


@app.route('/company/login', methods = ['POST', 'GET'])
def companyLogin():
    if request.method == 'POST':
        
        company_email = request.form['company_email']
        company_password = request.form['password']

        sql = 'select * from companies where company_email = %s'

        connection = pymysql.connect(host='localhost', user='root',password='', database='hustle_db' )
        cursor = connection.cursor()
        cursor.execute(sql, company_email)

        count = cursor.rowcount
        if count == 0:
            return render_template('company/login.html', error = 'Company Email not Found')
        else:
            company = cursor.fetchone()
            hashed_password = company[9]
            if hash_verify(company_password, hashed_password):
                session['company_key'] = company[1]            
                session['id'] = company[0]   
                session['company_email'] = company[2]  
                session['company_logo_pic'] = company[3]
                session['key'] = "company" 
                                    

                return redirect('/company/dashboard')
            else:
                return render_template('company/login.html', error = 'Invalid Password')
    else:
        return render_template('company/login.html', message = 'Login To Company Account')
    

@app.route('/candidate/dashboard')
@login_required
def candidate_dashboard():
    if session['key'] == "candidate" :
        categories=category_tags()
        locations = get_locations()
        jobType = get_jobType()
        salaryRange = get_salaryRange()
        return render_template('newCandidate/index.html',categories=categories,locations=locations,jobTypes=jobType)
    else:
       return render_template('403.html')
# NOT IN USE 
# @app.route('/candidate/profile')
# @login_required
# def candidate_profile():
#     if session['key'] == "candidate" :
#         skills = get_skills()
#         languages = get_languages()
#         softskills = get_soft_skills()
#         # User Profile
#         connection = pymysql.connect(host='localhost', user='root', password='', database='hustle_db')
#         sql2 = "SELECT * FROM candidates WHERE id = %s"
#         cursor2 = connection.cursor()
#         cursor2.execute(sql2, session['candidate_key'])
#         candidate = cursor2.fetchone()

#         if candidate:
#             session['fname'] = candidate[2]
#             session['lname'] = candidate[3]
#             session['surname'] = candidate[4]
#             session['phone'] = candidate[5]
#             session['title'] = candidate[9]
#             session['gender'] = candidate[10]
#             session['dob'] = candidate[11]
#             session['national_id_no'] = candidate[12]
#             session['address'] = candidate[13]
#             session['bio'] = candidate[14]
#             session['profile_pic'] = candidate[8]

#         # Work experience 
#         sql = "SELECT * FROM workexperiences WHERE candidate_id = %s"
#         cursor = connection.cursor()
#         cursor.execute(sql, session['candidate_key'])
#         work_experience = cursor.fetchone()

#         if work_experience:
#             session['company_name'] = work_experience[2]
#             session['job_title'] = work_experience[3]
#             session['from_date'] = work_experience[4]
#             session['to_date'] = work_experience[5]
#             session['description'] = work_experience[6]

#         # Certifications
#         sql = "SELECT * FROM certifications WHERE candidate_id = %s"
#         cursor1 = connection.cursor()
#         cursor1.execute(sql, session['candidate_key'])
#         certifications = cursor1.fetchone()

#         if certifications:
#             session['certification_name'] = certifications[2]
#             session['date_awarded'] = certifications[3]
#             session['desc'] = certifications[4]        

#         return render_template('candidate/components/profile.html', skills = skills, softskills = softskills , languages = languages)
#     else:        
#        return render_template('403.html')

@app.route('/company/dashboard')
@login_required
def company_dashboard():
   if session['key'] == "company" : 
        company_id = session['id']
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        sql= 'select * from postedjobs where company_id = %s'
        cursor.execute(sql,(company_id))
        jobs=cursor.fetchall()
        jobcount=len(jobs) 

        #  count the 
        sql = '''
        SELECT candidate_id FROM postedjobs pj JOIN postedjobs_candidates pjc ON pj.id = pjc.postedjob_id
        WHERE pj.company_id = %s
        '''        
        cursor.execute(sql, (company_id,))
        applications = cursor.fetchall()
        applications=len(applications)
        return render_template('company/dashboard.html',jobcounts=jobcount,job_applicants=applications)
   else:
       return render_template('403.html')

@app.route('/company/profile', methods=['POST', 'GET'])
@login_required
def company_profile():
    if session['key'] == "company" : 
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        company_id = session['id']
        if request.method == 'POST':
            company_name = request.form.get('company_name')
            company_email = request.form.get('company_email')
            company_phone = request.form.get('company_phone')
            company_location = request.form.get('company_location')
            admin_fname = request.form.get('admin_fname')  
            admin_lname = request.form.get('admin_lname')
            admin_surname = request.form.get('admin_surname')
            admin_phone = request.form.get('admin_phone')  
            company_description = request.form.get('company_description')  

            company_logo = request.files['company_logo']

            if  admin_phone == 'None' or admin_phone == '':
                flash('Admin phone number is required.', 'danger')
                return redirect(url_for('company_profile'))
            
            if company_logo and company_logo.filename != '':
                filename = secure_filename(company_logo.filename)
                logo_path = os.path.join('static/company_logos', filename)
                company_logo.save(logo_path)

                sql = """
                    UPDATE companies
                    SET company_name=%s, company_email=%s, company_phone=%s, company_location=%s, 
                        admin_fname=%s, admin_lname=%s, admin_surname=%s, admin_phone=%s, 
                        company_description=%s, company_logo=%s
                    WHERE id=%s
                """
                cursor.execute(sql, (
                    company_name, company_email, company_phone, company_location, 
                    admin_fname, admin_lname, admin_surname, admin_phone, 
                    company_description, filename, company_id
                ))
            else:
                sql = """
                    UPDATE companies
                    SET company_name=%s, company_email=%s, company_phone=%s, company_location=%s, 
                        admin_fname=%s, admin_lname=%s, admin_surname=%s, admin_phone=%s, 
                        company_description=%s
                    WHERE id=%s
                """
                cursor.execute(sql, (
                    company_name, company_email, company_phone, company_location, 
                    admin_fname, admin_lname, admin_surname, admin_phone, 
                    company_description, company_id
                ))
            connection.commit()
            connection.close()
            flash('Profile updated successfully','success')
            return redirect(url_for('company_profile'))

        else:
            sql = 'SELECT * FROM companies WHERE id=%s'
            cursor.execute(sql, company_id)
            company_pro = cursor.fetchone()
            connection.close()
            return render_template('/company/company-profile.html', profile=company_pro)
    else:
        return render_template('403.html')
   
@app.route('/company/postjob', methods=['POST', 'GET'])
@login_required
def postjob():
    
    if session['key'] == "company" :        
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        if request.method == 'POST' :
            job_title = request.form.get('job_title')
            job_location_id = request.form.get('job_location_id')
            jobtype_id = request.form.get('jobtype_id')
            salary_range_id = request.form.get('salary_range_id')
            job_skills = request.form.getlist('job_skills[]')  
            job_description = request.form.get('job_description')
            company_id = session['id']
            
            if len(job_title) <= 0:
                flash('Job Title Cannot be Empty', 'danger')
                return redirect(url_for('postjob'))
            if len(job_location_id) <= 0:
                flash('Job Location Cannot be Empty', 'danger')
                return redirect(url_for('postjob'))
            if len(jobtype_id) <= 0:
                flash('Job Type Cannot be Empty', 'danger')
                return redirect(url_for('postjob'))
            if len(salary_range_id) <= 0:
                flash('Salary Range Cannot be Empty', 'danger')
                return redirect(url_for('postjob'))
            if len(job_skills) <= 0:
                flash('Job Skills Cannot be Empty', 'danger')
                return redirect(url_for('postjob'))
            if len(job_description) <= 0:
                flash('Job Description Cannot be Empty', 'danger')
                return redirect(url_for('postjob'))
            else:
                job_data = (job_title, job_location_id, jobtype_id, salary_range_id, job_description, company_id)
                job_sql = 'INSERT INTO postedjobs (job_title, job_location_id, jobtype_id, salary_range_id, job_description, company_id) VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(job_sql, job_data)
                connection.commit()

                # Get the last inserted job id
                posted_job_id = cursor.lastrowid
                # Get the last inserted job id
                posted_job_id = cursor.lastrowid

                skill_sql = 'INSERT INTO  postedjobs_skills (posted_job_id, skill_id) VALUES (%s, %s)'
                for skill_id in job_skills:
                    cursor.execute(skill_sql, (posted_job_id, skill_id))
                connection.commit()
                flash("Job Posted Successfully", 'success')
                return redirect(url_for('postjob'))
        else:
            locations = get_job_locations()
            jobType = get_jobType()
            salaryRange = get_salaryRange()
            skills = get_skills()
            return render_template('company/post-jobs.html', locations=locations, jobType=jobType, salaryRange=salaryRange, skills=skills)
    else:
        return render_template('403.html')

#make search for user posted jobs
@app.route('/company/search', methods=['POST','GET'])
@login_required
def company_search():
    if session['key'] == "company" :      
        locations = get_job_locations()
        jobType = get_jobType()
        salaryRange = get_salaryRange()
        skills = get_skills()
        job_title = request.form.get('job_title')
        page = int(request.form.get('currentPage', 1))
        company_posted_jobs = get_company_posted_jobs(session['id'],job_title=job_title)
        per_page = 5
        pages = math.ceil(len(company_posted_jobs) / per_page)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_data = company_posted_jobs[start:end]
        print("company posted jobs are", paginated_data)
        return jsonify({'htmlresponse': render_template('company/components/posted_jobs.html', postedJobs=paginated_data, page = page, per_page =per_page, total = pages, locations=locations, jobType=jobType, salaryRange=salaryRange, skills=skills)})
    else:
        return render_template('403.html')
#getting applications
@app.route('/company/search/applications', methods=['POST','GET'])
@login_required
def company_search_applications():
    if session['key'] == "company" :      
        locations = get_job_locations()
        jobType = get_jobType()
        salaryRange = get_salaryRange()
        skills = get_skills()
        job_title = request.form.get('job_title')
        page = int(request.form.get('currentPage', 1))
        company_posted_jobs = get_company_posted_jobs(session['id'],job_title=job_title)
        per_page = 5
        pages = math.ceil(len(company_posted_jobs) / per_page)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_data = company_posted_jobs[start:end]
        # print("company posted jobs are", paginated_data)
        return jsonify({'htmlresponse': render_template('company/components/applications.html', postedJobs=paginated_data, page = page, per_page =per_page, total = pages, locations=locations, jobType=jobType, salaryRange=salaryRange, skills=skills)})
    else:
            return render_template('403.html')

#getting applicants
@app.route('/company/search/applicants/<int:job_id>', methods=['POST','GET'])
@login_required
def company_search_applicants(job_id):
    if session['key'] == "company" :
        professional_title = request.form.get('professional_title')
    
        applicants= get_applicants(job_id,professional_title)    
       
        page = int(request.form.get('currentPage', 1))        
        per_page = 5
        pages = math.ceil(len(applicants) / per_page)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_data = applicants[start:end]
        print("company posted jobs are", paginated_data)
        return jsonify({'htmlresponse': render_template('company/components/applicants.html',job_id=job_id,professional_title=professional_title,applicants=paginated_data, page = page, per_page =per_page, total = pages)})
    else:
        return render_template('403.html')


# #geting job applicants
# @app.route('/jobs/applicants/<int:job_id>')
# @login_required
# def job_applicants(job_id):
#     if session['key'] == "company" : 
#         applicants= get_applicants(job_id)
#         return render_template("/company/applicants.html",job_id=job_id,applicants=applicants)
#     else:
#             return render_template('403.html')
@app.route('/jobs/applicants/<int:job_id>')
@login_required
def job_applicants(job_id):
    if session.get('key') != "company":
        return render_template('403.html')

    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        # Get list of applicants for the job
        applicants = get_applicants(job_id)

        # Fetch detailed information for each applicant
        detailed_applicants = []
        for applicant in applicants:
            candidate_id = applicant[0]  # Assuming first element is candidate_id
            candidate_info = fetch_additional_info(cursor, candidate_id)
            detailed_applicants.append({
                'candidate_pro': candidate_info['candidate_pro'],
                'technical_skills': candidate_info['technical_skills'],
                'soft_skills': candidate_info['soft_skills'],
                'languages': candidate_info['languages'],
                'work_experiences': candidate_info['work_experiences'],
                'certifications': candidate_info['certifications']
            })

        return render_template("/company/applicants.html", job_id=job_id, applicants=detailed_applicants)

    except Exception as e:
        flash(f'An error occurred while fetching applicants: {str(e)}', 'danger')
        return redirect(url_for('home'))

    finally:
        connection.close()


#geting job applicants
@app.route('/candidate/applyjob/<int:job_id>')
@login_required
def apply_job(job_id):
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    if session['key'] == "candidate" : 
        cadidate_id=session['candidate_key']
        mysql = "select * from postedjobs_candidates where postedjob_id =%s and candidate_id=%s"
        cursor.execute(mysql, (job_id,cadidate_id))
        if cursor.rowcount == 0:
            sql='insert into postedjobs_candidates(postedjob_id,candidate_id) values (%s,%s)'
            cursor.execute(sql,(job_id,cadidate_id))
            connection.commit()
            flash("Job Applied Successfully", 'success')
            return redirect(url_for('candidate_dashboard'))
        else:
            flash("You have already Applied for this Job", 'success')
            return redirect(url_for('candidate_dashboard'))
    else:
        return render_template('403.html')

#fetching data for editing jobs 
@app.route('/company/editjob/<int:job_id>', methods=['GET'])

def edit_job(job_id):
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    
    job_sql = '''
    SELECT id, job_title, job_location_id, jobtype_id, salary_range_id, job_description, updated_at, 
           (SELECT location_name FROM locations WHERE id = postedjobs.job_location_id) as job_location_name, 
           (SELECT jobtype_name FROM jobtypes WHERE id = postedjobs.jobtype_id) as jobtype_name, 
           (SELECT salary_range FROM salaryranges WHERE id = postedjobs.salary_range_id) as salary_range
    FROM postedjobs 
    WHERE id = %s
    '''
    cursor.execute(job_sql, (job_id,))
    job_data = cursor.fetchone()

    skill_sql = 'SELECT skill_name FROM skills JOIN postedjobs_skills ON skills.id = postedjobs_skills.skill_id WHERE postedjobs_skills.posted_job_id = %s'
    cursor.execute(skill_sql, (job_id,))
    job_skills = [skill[0] for skill in cursor.fetchall()]
    
    # Convert job_data to a dictionary
    job_dict = {
        'job_id': job_data[0],
        'job_title': job_data[1],
        'job_location_id': job_data[2],
        'jobtype_id': job_data[3],
        'salary_range_id': job_data[4],
        'job_description': job_data[5],
        'job_location_name': job_data[7],
        'jobtype_name': job_data[8],
        'salary_range_name': job_data[9],
        'date':job_data[6],
        'job_skills': job_skills
    }

    return jsonify(job_dict)

#deleting jobs 
@app.route('/company/deletejob/', methods=['POST'])
@login_required
def deletejob():
    job_id=request.form.get('job_id')
    if request.method == "POST":
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        try:
            delete_job_query ='''DELETE FROM `postedjobs` WHERE id = %s'''
            cursor.execute(delete_job_query, (job_id,))
            delete_skill_query = '''DELETE FROM postedjobs_skills WHERE posted_job_id=%s'''
            cursor.execute(delete_skill_query, (job_id,))
            connection.commit()
            flash("Job Deleted Successfully", 'success')
            # return redirect(url_for('postjob'))
        except Exception as e:
            connection.rollback()
            flash("Job Not Deleted Successfully: " + str(e), 'danger')

        finally:
                cursor.close()
                connection.close()
    else:
        flash("Job ID is missing", 'danger')

    return redirect(url_for('postjob'))


@app.route('/company/applications')
@login_required
def company_applications():
    if session['key'] == "company" :
        company_id = session['id']
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        sql = '''
        SELECT  job_title, COUNT(pjc.candidate_id) AS application_count
        FROM postedjobs pj
        LEFT JOIN postedjobs_candidates pjc ON pj.id = pjc.postedjob_id
        WHERE pj.company_id = %s
        GROUP BY pj.id, pj.job_title
        '''
        cursor.execute(sql, (company_id,))
        job_applications = cursor.fetchall()
        # job_applications_dict = {job['job_id']: job['application_count'] for job in job_applications}
        print(job_applications)
        
        return render_template('/company/applications.html',job_application=job_applications)
    else:
        return render_template('403.html')


@app.route('/company/logout')
def companylogout():
    session.clear()
    return redirect('/company/login')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/candidate/login')

# comment# about us
@app.route('/aboutus')
def about():
    return render_template('about.html')

# UPDATED VERSION OF CANDIDATE PROFILE 
# CANDIDATE PROFILE   
@app.route('/candidate/profile', methods=['POST', 'GET'])
@login_required
def candidate_profile():
    if session.get('key') != "candidate":
        flash('Unauthorized access or session key not set correctly.', 'warning')
        return redirect(url_for('home'))

    candidate_id = session.get('candidate_key')
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        # Fetch candidate profile and additional info
        candidate_info = fetch_additional_info(cursor, candidate_id)

        return render_template('newCandidate/candidateProfile.html', profile=candidate_info['candidate_pro'],
                               technical_skills=candidate_info['technical_skills'],
                               soft_skills=candidate_info['soft_skills'],
                               languages=candidate_info['languages'],
                               work_experiences=candidate_info['work_experiences'],
                               certifications=candidate_info['certifications'])
    except Exception as e:
        flash(f'An error occurred while fetching the profile: {str(e)}', 'danger')
        return redirect(url_for('home'))
    finally:
        connection.close()



# EDIT CANDIDATE PROFILE 
@app.route('/candidate/edit-profile', methods=['POST', 'GET'])
@login_required
def update_profile():
    if session.get('key') != "candidate":
        return render_template('403.html')

    candidate_id = session.get('candidate_key')
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        firstname = request.form['fname']
        lastname = request.form['lname']
        surname = request.form['surname']
        phone = request.form['phone']
        title = request.form['professional_title']
        gender = request.form['gender']
        dob = request.form['dob']
        national_id_no = request.form['national_id_no']
        address = request.form['address']
        bio = request.form['bio']

        data = (firstname, lastname, surname, phone, title, gender, dob, national_id_no, address, bio, candidate_id)

        try:
            sql = """
                UPDATE candidates 
                SET fname = %s, lname = %s, surname = %s, phone = %s, professional_title = %s, gender = %s, dob = %s, national_id_no = %s, address = %s, bio = %s 
                WHERE id = %s
            """
            cursor.execute(sql, data)
            connection.commit()
            flash('Profile updated successfully', 'success')
        except Exception as e:
            connection.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            connection.close()

        return redirect(url_for('update_profile'))

    else:
        try:
            # Fetch additional info
            additional_info = fetch_additional_info(cursor, candidate_id)

            return render_template('newCandidate/edit-profile.html',
                                   
                                profile=additional_info['candidate_pro'],
                                skills=additional_info['technical_skills'],
                                softskills=additional_info['soft_skills'],
                                languages=additional_info['languages'],
                                unselected_skills=additional_info['unselected_skills'],
                                unselected_soft_skills=additional_info['unselected_soft_skills'],
                                unselected_languages=additional_info['unselected_languages'],
                                work_experiences=additional_info['work_experiences'],
                                certifications=additional_info['certifications'])

        except Exception as e:
            flash(f'An error occurred while fetching the profile: {str(e)}', 'danger')
            return redirect(url_for('home'))
        finally:
            connection.close()
# EDIT CANDIDATE PROFILE BY ID
@app.route('/candidate/profile/<int:candidate_id>', methods=['GET'])
@login_required
def candidate_profile_id(candidate_id):
    if session.get('key') not in ["candidate", "company", "admin"]:
        return jsonify({'error': 'Unauthorized access or session key not set correctly.'}), 403

    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        candidate_info = fetch_additional_info(cursor, candidate_id)

        if not candidate_info['candidate_pro']:
            return jsonify({'error': 'Candidate not found.'}), 404

        return jsonify(candidate_info)
    except Exception as e:
        return jsonify({'error': f'An error occurred while fetching the profile: {str(e)}'}), 500
    finally:
        connection.close()



# UPLOAD PHOTO
@app.route('/candidate/upload-photo', methods=['GET', 'POST'])
@login_required
def upload_photo():
    if session['key'] == "candidate" :
        if request.method == 'POST':
            if 'profile_pic' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['profile_pic']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                # Update the candidate profile picture in the database
                connection = pymysql.connect(host='localhost', user='root', password='', database='hustle_db')
                cursor = connection.cursor()
                sql = "UPDATE candidates SET profile_pic = %s WHERE id = %s"
                cursor.execute(sql, (filename,session['candidate_key']))
                connection.commit()

                flash('Profile picture updated successfully!', 'success')
                return redirect(url_for('update_profile'))
        return render_template('newCandidate/profile-pic-upload.html')
    else:
        return render_template('403.html')
    

# UPLOAD CANDIDATE CV UPLOAD
@app.route('/candidate/upload-cv', methods=['POST', 'GET'])
@login_required
def upload_cv():
    if session.get('key') == "candidate":
        if request.method == 'POST':
            cv_file = request.files.get('cv_upload')
            if cv_file and cv_file.filename:
                filename = secure_filename(cv_file.filename)
                cv_path = os.path.join('static/cv_files', filename)

                try:
                    connection = pymysql.connect(**db_config)
                    cursor = connection.cursor()

                    # Retrieve the current CV file path
                    sql = "SELECT cv_upload FROM candidates WHERE id = %s"
                    cursor.execute(sql, (session.get('candidate_key'),))
                    old_cv = cursor.fetchone()

                    # Save the new CV file
                    cv_file.save(cv_path)

                    # Update the candidate's CV path in the database
                    sql = "UPDATE candidates SET cv_upload = %s WHERE id = %s"
                    cursor.execute(sql, (filename, session.get('candidate_key')))
                    connection.commit()

                    # Delete the old CV file
                    if old_cv and old_cv[0]:
                        old_cv_path = os.path.join('static/cv_files', old_cv[0])
                        if os.path.exists(old_cv_path):
                            os.remove(old_cv_path)

                    flash('CV uploaded successfully!', 'success')
                except Exception as e:
                    connection.rollback()
                    flash(f'An error occurred: {str(e)}', 'danger')
                finally:
                    connection.close()
                
                return redirect(url_for('update_profile'))
            else:
                flash('No CV file selected.', 'danger')
        
        return render_template('newCandidate/profile-cv-upload.html')
    else:
        return render_template('403.html')
    

# ADD CANDIDATE SOFT SKILLS
@app.route('/candidate/add-soft-skill', methods=['POST'])
@login_required
def add_soft_skill():
    if session.get('key') != "candidate":
        return render_template('403.html')
    
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    candidate_id = session.get('candidate_key')

    try:
        # Get the selected soft skills from the form
        selected_soft_skills = request.form.getlist('soft_skills[]')

        if not selected_soft_skills:
            flash('No soft skills selected', 'danger')
            return redirect(url_for('update_profile'))

        # Filter out any invalid or empty values
        valid_soft_skills = [int(skill_id) for skill_id in selected_soft_skills if skill_id.isdigit()]

        if not valid_soft_skills:
            flash('Invalid soft skills selected', 'danger')
            return redirect(url_for('update_profile'))

        # Insert the selected soft skills into the database
        softskills_sql = 'INSERT INTO candidates_softskills (candidate_id, softskill_id) VALUES (%s, %s)'
        for soft_skill_id in valid_soft_skills:
            cursor.execute(softskills_sql, (candidate_id, soft_skill_id))
        
        connection.commit()
        flash('Soft skills added successfully', 'success')

    except Exception as e:
        connection.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')

    finally:
        connection.close()

    return redirect(url_for('update_profile'))

# ADD CANDIDATE TECHNICAL SKILLS
@app.route('/candidate/add-technical-skill', methods=['POST'])
@login_required
def add_technical_skill():
    if session.get('key') != "candidate":
        return render_template('403.html')
    
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    candidate_id = session.get('candidate_key')

    try:
        # Get the selected technical skills from the form
        selected_technical_skills = request.form.getlist('technical_skills[]')

        if not selected_technical_skills:
            flash('No technical skills selected', 'danger')
            return redirect(url_for('update_profile'))

        # Filter out any invalid or empty values
        valid_technical_skills = [int(skill_id) for skill_id in selected_technical_skills if skill_id.isdigit()]

        if not valid_technical_skills:
            flash('Invalid technical skills selected', 'danger')
            return redirect(url_for('update_profile'))

        # Insert the selected technical skills into the database
        technicalskills_sql = 'INSERT INTO candidates_technicalskills (candidate_id, skill_id) VALUES (%s, %s)'
        for technical_skill_id in valid_technical_skills:
            cursor.execute(technicalskills_sql, (candidate_id, technical_skill_id))
        
        connection.commit()
        flash('Technical skills added successfully', 'success')

    except Exception as e:
        connection.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')

    finally:
        connection.close()

    return redirect(url_for('update_profile'))

# ADD CANDIDATE LANGUAGES
@app.route('/candidate/add-language', methods=['POST'])
@login_required
def add_language():
    if session.get('key') != "candidate":
        return render_template('403.html')
    
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    candidate_id = session.get('candidate_key')

    try:
        # Get the selected languages from the form
        selected_languages = request.form.getlist('languages[]')

        if not selected_languages:
            flash('No languages selected', 'danger')
            return redirect(url_for('update_profile'))

        # Filter out any invalid or empty values
        valid_languages = [int(language_id) for language_id in selected_languages if language_id.isdigit()]

        if not valid_languages:
            flash('Invalid languages selected', 'danger')
            return redirect(url_for('update_profile'))

        # Insert the selected languages into the database
        languages_sql = 'INSERT INTO candidates_languages (candidate_id, language_id) VALUES (%s, %s)'
        for language_id in valid_languages:
            cursor.execute(languages_sql, (candidate_id, language_id))
        
        connection.commit()
        flash('Languages added successfully', 'success')

    except Exception as e:
        connection.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')

    finally:
        connection.close()

    return redirect(url_for('update_profile'))



# ADD CANDIDATE CERTIFICATION
@app.route('/candidate/add-certification', methods=['POST'])
@login_required
def add_certification():
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    if session['key'] == "candidate":
        if request.method == 'POST':
            certification_name = request.form['certification_name']
            date_awarded = request.form['date_awarded']
            description = request.form['description']

            data = (session['candidate_key'], certification_name, date_awarded, description)
            sql = "INSERT INTO certifications (candidate_id, certification_name, date_awarded, description) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, data)
            connection.commit()

            flash('Certification added successfully', 'success')
            return redirect(url_for('update_profile'))

    else:
        return render_template('403.html')
    
# GET CANDIDATE CERTIFICATIONS
@app.route('/candidate/get-certifications', methods=['POST'])
@login_required
def get_certifications():
    current_page = int(request.form['currentPage'])
    items_per_page = int(request.form['itemsPerPage'])
    candidate_id = session.get('candidate_key')

    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT * FROM certifications WHERE candidate_id = %s LIMIT %s OFFSET %s"
    cursor.execute(sql, (candidate_id, items_per_page, (current_page - 1) * items_per_page))
    certifications = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) as total FROM certifications WHERE candidate_id = %s", (candidate_id,))
    total_certifications = cursor.fetchone()['total']
    total_pages = (total_certifications + items_per_page - 1) // items_per_page

    htmlresponse = ""
    for certification in certifications:
        htmlresponse += render_template('certification_row.html', certification=certification)

    return jsonify({
        'htmlresponse': htmlresponse,
        'currentPage': current_page,
        'total': total_certifications,
        'totalPages': total_pages
    })
 

# UPDATE CANDIDATE CERTIFICATION
@app.route('/candidate/update-certifications', methods=['POST'])
@login_required
def update_certification():
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    if session['key'] == "candidate":
        if request.method == 'POST':
            certification_id = request.form['id']
            certification_name = request.form['certification_name']
            date_awarded = request.form['date_awarded']
            description = request.form['description']

            data = (certification_name, date_awarded, description, certification_id)
            sql = "UPDATE certifications SET certification_name = %s, date_awarded = %s, description = %s WHERE id = %s AND candidate_id = %s"
            cursor.execute(sql, data + (session['candidate_key'],))
            connection.commit()

            flash('Certification updated successfully', 'success')
            return redirect(url_for('update_profile'))

    else:
        return render_template('403.html')


    
# DELETE CANDIDATE CERTIFICATION
@app.route('/candidate/delete-certification/<int:id>', methods=['POST'])
@login_required
def delete_certification(id):
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    if session['key'] == "candidate":
        sql = "DELETE FROM certifications WHERE id = %s"
        cursor.execute(sql, (id))
        connection.commit()
        flash('Certification deleted successfully', 'success')
        return redirect(url_for('update_profile'))
    else:
        return render_template('403.html')
    
# GET CANDIDATE WORK EXPERIENCE
@app.route('/candidate/get-work-experience', methods=['POST'])
@login_required
def get_work_experience():
    current_page = int(request.form['currentPage'])
    items_per_page = int(request.form['itemsPerPage'])
    candidate_id = session.get('candidate_key')

    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    sql = "SELECT * FROM workexperiences WHERE candidate_id = %s LIMIT %s OFFSET %s"
    cursor.execute(sql, (candidate_id, items_per_page, (current_page - 1) * items_per_page))
    work_experiences = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) as total FROM workexperiences WHERE candidate_id = %s", (candidate_id,))
    total_work_experiences = cursor.fetchone()['total']
    total_pages = (total_work_experiences + items_per_page - 1) // items_per_page

    htmlresponse = ""
    for work_experience in work_experiences:
        htmlresponse += render_template('work_experience_row.html', work_experience=work_experience)

    return jsonify({
        'htmlresponse': htmlresponse,
        'currentPage': current_page,
        'total': total_work_experiences,
        'totalPages': total_pages
    })




# ADD CANDIDATE WORK EXPERIENCE
@app.route('/candidate/add-work-experience', methods=['POST'])
@login_required
def add_work_experience():
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    if session['key'] == "candidate":
        if request.method == 'POST':
            company_name = request.form['company_name']
            job_title = request.form['job_title']
            from_date = request.form['from_date']
            to_date = request.form['to_date']
            description = request.form['description']

            data = (session['candidate_key'], company_name, job_title, from_date, to_date, description)
            sql = "INSERT INTO workexperiences (candidate_id, company_name, job_title, from_date, to_date, description) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, data)
            connection.commit()

            flash('Work experience added successfully', 'success')
            return redirect(url_for('update_profile'))

    else:
        return render_template('403.html')
    
# UPDATE CANDIDATE WORK EXPERIENCE
@app.route('/candidate/update-work-experience', methods=['POST'])
@login_required
def update_work_experience():
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    if session['key'] == "candidate":
        if request.method == 'POST':
            work_experience_id = request.form['id']
            company_name = request.form['company_name']
            job_title = request.form['job_title']
            from_date = request.form['from_date']
            to_date = request.form['to_date']
            description = request.form['description']

            data = (company_name, job_title, from_date, to_date, description, work_experience_id)
            sql = "UPDATE workexperiences SET company_name = %s, job_title = %s, from_date = %s, to_date = %s, description = %s WHERE id = %s AND candidate_id = %s"
            cursor.execute(sql, data + (session['candidate_key'],))
            connection.commit()

            flash('Work experience updated successfully', 'success')
            return redirect(url_for('update_profile'))

    else:
        return render_template('403.html')

# DELETE CANDIDATE WORK EXPERIENCE
@app.route('/candidate/delete-work-experience/<int:id>', methods=['POST'])
@login_required
def delete_work_experience(id):
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    if session['key'] == "candidate":
        sql = "DELETE FROM workexperiences WHERE id = %s"
        cursor.execute(sql, (id))
        connection.commit()
        flash('Work experience deleted successfully', 'success')
        return redirect(url_for('update_profile'))
    else:
        return render_template('403.html')

 
# DELETE CANDIDATE TECHNICAL SKILLS
@app.route('/candidate/delete-skill/<int:skill_id>', methods=['POST'])
@login_required
def delete_technical_skill(skill_id):
    if session.get('key') != "candidate":
        return render_template('403.html')

    candidate_id = session.get('candidate_key')

    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    try:
        sql = 'DELETE FROM candidates_technicalskills WHERE candidate_id=%s AND skill_id=%s'
        cursor.execute(sql, (candidate_id, skill_id))
        connection.commit()
        flash('Technical skill deleted successfully', 'success')
    except Exception as e:
        connection.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('update_profile'))

# DELETE CANDIDATE SOFT SKILLS
@app.route('/candidate/delete-softskill/<int:softskill_id>', methods=['POST'])
@login_required
def delete_soft_skill(softskill_id):
    if session.get('key') != "candidate":
        return render_template('403.html')

    candidate_id = session.get('candidate_key')

    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    try:
        sql = 'DELETE FROM candidates_softskills WHERE candidate_id=%s AND softskill_id=%s'
        cursor.execute(sql, (candidate_id, softskill_id))
        connection.commit()
        flash('Soft skill deleted successfully', 'success')
    except Exception as e:
        connection.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('update_profile'))



# DELETE CANDIDATE LANGUAGES
@app.route('/candidate/delete-language/<int:language_id>', methods=['POST'])
@login_required
def delete_language(language_id):
    if session.get('key') != "candidate":
        return render_template('403.html')

    candidate_id = session.get('candidate_key')

    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    try:
        sql = 'DELETE FROM candidates_languages WHERE candidate_id=%s AND language_id=%s'
        cursor.execute(sql, (candidate_id, language_id))
        connection.commit()
        flash('Language deleted successfully', 'success')
    except Exception as e:
        connection.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('update_profile'))

# Admin Functions

@app.route('/admin/login', methods = ['POST', 'GET'])
def adminLogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        sql = 'select * from admins where email = %s'

        connection = pymysql.connect(host='localhost', user='root',password='', database='hustle_db' )
        cursor = connection.cursor()
        cursor.execute(sql, email)

        count = cursor.rowcount
        if count == 0:
            return render_template('admin/login.html', error = 'Incorrect Login Credentilals')
        else:
            admin = cursor.fetchone()
            hashed_password = admin[5]
            if hash_verify(password, hashed_password):
                session['admin_key'] = admin[0]
                session['email'] = admin[4]
                session['fname'] = admin[1]
                session['surname'] = admin[3]
                session['admin_profile_pic'] = admin[8]
                session['key'] = "admin"

                return redirect('/admin/dashboard')
            
            else:
                return render_template('admin/login.html', error = 'Incorrect Login Credentilals')
    else:
        return render_template('admin/login.html', message = 'Login Below')
    

@app.route('/admin/logout')
def adminlogout():
    session.clear()
    return redirect('/')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if session['key'] == "admin":
        connection = pymysql.connect(host='localhost', user='root',password='', database='hustle_db' )
        cursor = connection.cursor()

        companies_sql = "SELECT COUNT(*) AS total_count FROM companies"
        cursor.execute(companies_sql)
        companies = cursor.fetchone()[0]

        candidates_sql = "SELECT COUNT(*) AS total_count FROM candidates"
        cursor.execute(candidates_sql)
        candidates = cursor.fetchone()[0]

        jobs_sql = "SELECT COUNT(*) AS total_count FROM postedjobs"
        cursor.execute(jobs_sql)
        jobs = cursor.fetchone()[0]

        return render_template('admin/dashboard.html',jobs=jobs,candidates=candidates,companies=companies, current_path=request.path)
    else:
       return render_template('403.html')

@app.route('/admin/view-companies')
@login_required
def view_companies():
    if session['key'] == "admin" :
        companies = get_allcompanies()

        return render_template('admin/companies.html', companies=companies, current_path=request.path)
    else:
       return render_template('403.html')

@app.route('/admin/view-candidates')
@login_required
def view_candidates():
    if session['key'] == "admin" :
        candidates= get_candidates()

        return render_template('admin/candidates.html', candidates=candidates, current_path=request.path)
    else:
       return render_template('403.html')

@app.route('/admin/view-jobs')
@login_required
def view_jobs():
    if session['key'] == "admin" :
        jobs = get_featured_jobs()

        return render_template('admin/jobs.html',jobs=jobs, current_path=request.path)
    else:
       return render_template('403.html')

if __name__ == '__main__':
    app.debug = True
    app.run()