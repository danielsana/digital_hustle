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
                return render_template('candidate/login.html', error = 'Password Not Found')
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

        return render_template('candidate/dashboard.html',categories=categories,locations=locations,jobTypes=jobType)
    else:
       return render_template('403.html')

@app.route('/candidate/profile')
@login_required
def candidate_profile():
    if session['key'] == "candidate" :
        skills = get_skills()
        languages = get_languages()
        softskills = get_soft_skills()
        # User Profile
        connection = pymysql.connect(host='localhost', user='root', password='', database='hustle_db')
        sql2 = "SELECT * FROM candidates WHERE id = %s"
        cursor2 = connection.cursor()
        cursor2.execute(sql2, session['candidate_key'])
        candidate = cursor2.fetchone()

        if candidate:
            session['fname'] = candidate[2]
            session['lname'] = candidate[3]
            session['surname'] = candidate[4]
            session['phone'] = candidate[5]
            session['title'] = candidate[9]
            session['gender'] = candidate[10]
            session['dob'] = candidate[11]
            session['national_id_no'] = candidate[12]
            session['address'] = candidate[13]
            session['bio'] = candidate[14]
            session['profile_pic'] = candidate[8]

        # Work experience 
        sql = "SELECT * FROM workexperiences WHERE candidate_id = %s"
        cursor = connection.cursor()
        cursor.execute(sql, session['candidate_key'])
        work_experience = cursor.fetchone()

        if work_experience:
            session['company_name'] = work_experience[2]
            session['job_title'] = work_experience[3]
            session['from_date'] = work_experience[4]
            session['to_date'] = work_experience[5]
            session['description'] = work_experience[6]

        # Certifications
        sql = "SELECT * FROM certifications WHERE candidate_id = %s"
        cursor1 = connection.cursor()
        cursor1.execute(sql, session['candidate_key'])
        certifications = cursor1.fetchone()

        if certifications:
            session['certification_name'] = certifications[2]
            session['date_awarded'] = certifications[3]
            session['desc'] = certifications[4]        

        return render_template('candidate/components/profile.html', skills = skills, softskills = softskills , languages = languages)
    else:        
       return render_template('403.html')

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


#geting job applicants
@app.route('/jobs/applicants/<int:job_id>')
@login_required
def job_applicants(job_id):
    if session['key'] == "company" : 
        applicants= get_applicants(job_id)
        return render_template("/company/applicants.html",job_id=job_id,applicants=applicants)
    else:
            return render_template('403.html')

#geting job applicants
@app.route('/candidate/applyjob/<int:job_id>')
@login_required
def apply_job(job_id):
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    if session['key'] == "candidate" : 
        cadidate_id=session['candidate_key']
        sql='insert into postedjobs_candidates(postedjob_id,candidate_id) values (%s,%s)'
        cursor.execute(sql,(job_id,cadidate_id))
        connection.commit()
        flash("Job Applied Successfully", 'success')
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

# update bio
@app.route('/candidate/update-bio',  methods = ['POST', 'GET'])
@login_required
def update_bio():
    if session['key'] == "candidate" :
        if request.method == 'POST':
            firstname = request.form['fname']
            lastname = request.form['lname']
            surname = request.form['surname']
            phone = request.form['phone']
            title = request.form['title']
            gender = request.form['gender']
            dob = request.form['dob']
            national_id_no = request.form['national_id_no']
            address = request.form['address']
            bio = request.form['bio']

            connection = pymysql.connect(host='localhost', user='root',password='', database='hustle_db' )
            cursor = connection.cursor()

            data = (firstname, lastname, surname, phone, title, gender, dob, national_id_no, address, bio,session['candidate_key'])

            sql = "update candidates set fname = %s, lname = %s, surname = %s, phone = %s, professional_title = %s, gender = %s, dob = %s, national_id_no = %s, address = %s, bio = %s where id = %s"
            cursor.execute(sql, data)
            connection.commit()           
            

            return render_template('candidate/components/profile.html', success = 'Bio Updated Successfully')

        else:
            return render_template('candidate/components/profile.html')
            
    else:
        return render_template('403.html')
    

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

                flash('Profile picture updated successfully!')
                return redirect(url_for('candidate_profile'))
        return render_template('candidate/profile-pic-upload.html')
    else:
        return render_template('403.html')
  

@app.route('/candidate/update-certifications', methods=['GET', 'POST'])
@login_required
def update_work_experience():
    if session['key'] == "candidate" :
        
        if request.method == 'POST':
            
            certification_name = request.form['certification_name']
            date_awarded = request.form['date_awarded']
            description = request.form['description']

            connection = pymysql.connect(host='localhost', user='root',password='', database='hustle_db' )
            cursor = connection.cursor()

            data = (session['candidate_key'], certification_name, date_awarded, description,session['candidate_key'])

            sql = "update certifications set candidate_id = %s, certification_name = %s, date_awarded = %s, description = %s  where candidate_id = %s"
            cursor.execute(sql, data)
            connection.commit()

            return render_template('candidate/components/profile.html', success = 'certifications Updated Successfully')

        else:
            return render_template('candidate/components/profile.html')
    
    else:
        return render_template('403.html')

@app.route('/candidate/update-work-experience', methods=['GET', 'POST'])
@login_required
def update_certifications():
    if session['key'] == "candidate" :        
        if request.method == 'POST':            
            company_name = request.form['company_name']
            job_title = request.form['job_title']
            from_date = request.form['from_date']
            to_date = request.form['to_date']
            description = request.form['description']
            connection = pymysql.connect(host='localhost', user='root',password='', database='hustle_db' )
            cursor = connection.cursor()
            data = (session['candidate_key'], company_name, job_title, from_date, to_date, description,session['candidate_key'])

            sql = "update workexperiences set candidate_id = %s, company_name = %s, job_title = %s, from_date = %s, to_date = %s, description = %s  where candidate_id = %s"
            cursor.execute(sql, data)
            connection.commit()

            return render_template('candidate/components/profile.html', success = 'workexperiences Updated Successfully')

        else:
            return render_template('candidate/components/profile.html')
    else:
        return render_template('403.html') 

@app.route('/candidate/update-skills-attributes', methods=['POST', 'GET'])
@login_required
def updateCandidateSkills():
    if session['key'] == "candidate" :
        skills = get_skills()
        languages = get_languages()
        softskills = get_soft_skills()
        
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        if request.method == 'POST':
            technical_skills = request.form.getlist('technical_skills[]')
            soft_skills = request.form.getlist('soft_skills[]')
            languages = request.form.getlist('languages[]')

            if len(technical_skills) <= 0:
                return render_template('candidate/components/profile.html', error='Technical skills cannot be empty')
            if len(soft_skills) <= 0:
                return render_template('candidate/components/profile.html', error='Soft skills cannot be empty')
            if len(languages) <= 0:
                return render_template('candidate/components/profile.html', error='Languages cannot be empty')

            # Assuming candidate ID is stored in session
            candidate_id = session.get('key')
            if not candidate_id:
                return render_template('candidate/components/profile.html', error='Candidate ID not found in session')

            technical_sql = 'INSERT INTO candidates_technicalskills (candidate_id, skill_id) VALUES (%s, %s)'
            softskills_sql = 'INSERT INTO candidates_softskills (candidate_id, softskill_id) VALUES (%s, %s)'
            languages_sql = 'INSERT INTO candidates_languages (candidate_id, language_id) VALUES (%s, %s)'

            try:
                for skill_id in technical_skills:
                    cursor.execute(technical_sql, (candidate_id, skill_id))
                
                for soft_skill_id in soft_skills:
                    cursor.execute(softskills_sql, (candidate_id, soft_skill_id))

                for language_id in languages:
                    cursor.execute(languages_sql, (candidate_id, language_id))
                
                connection.commit()
                return render_template('candidate/components/profile.html', skills = skills, softskills = softskills , languages = languages, success='Skills updated successfully')

            
            except Exception as e:
                connection.rollback()
                
                return render_template('candidate/components/profile.html', skills = skills, softskills = softskills , languages = languages, error=str(e))
                
        else:
            return render_template('candidate/components/profile.html')
    else:
        return render_template('403.html')

if __name__ == '__main__':
    app.debug = True
    app.run()