import os
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'school.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "fatima_secret_key_123"

db = SQLAlchemy(app)

# --- MODELS ---
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    student_class = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), nullable=False)
    result_class = db.Column(db.String(20))
    exam_term = db.Column(db.String(50))
    english = db.Column(db.Integer, default=0)
    maths = db.Column(db.Integer, default=0)
    urdu = db.Column(db.Integer, default=0)
    science = db.Column(db.Integer, default=0)
    islamiat = db.Column(db.Integer, default=0)
    computer = db.Column(db.Integer, default=0)
    physics = db.Column(db.Integer, default=0)
    chemistry = db.Column(db.Integer, default=0)
    phy_lab = db.Column(db.Integer, default=0)
    chem_lab = db.Column(db.Integer, default=0)
    bio_lab = db.Column(db.Integer, default=0)
    comp_lab = db.Column(db.Integer, default=0)

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feedback = db.Column(db.Text, nullable=False)

class PTM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    parent_info = db.Column(db.String(100))

# --- ATTENDANCE MODEL (roz ki) ---
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), nullable=False)
    student_name = db.Column(db.String(100))
    student_class = db.Column(db.String(20))
    date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(10), nullable=False)  # Present / Absent

# --- DISCIPLINE MODEL (monthly) ---
class Discipline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), nullable=False)
    student_name = db.Column(db.String(100))
    student_class = db.Column(db.String(20))
    month = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer, default=0)  # 0-100

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard/<role>')
def dashboard(role):
    session['role'] = role
    all_students = Student.query.all()
    all_complaints = Complaint.query.all()
    all_meetings = PTM.query.all()
    all_attendance = Attendance.query.order_by(Attendance.date.desc()).all()
    all_discipline = Discipline.query.order_by(Discipline.month.desc()).all()
    return render_template('dashboard.html',
                           students=all_students,
                           role=role,
                           complaints=all_complaints,
                           meetings=all_meetings,
                           attendance=all_attendance,
                           discipline=all_discipline)

@app.route('/add', methods=['POST'])
def add_student():
    if session.get('role') != 'admin':
        return "Access Denied!", 403
    existing = Student.query.filter_by(roll_no=request.form.get('roll_no')).first()
    if existing:
        return redirect(url_for('dashboard', role='admin'))
    new_s = Student(
        name=request.form.get('name'),
        roll_no=request.form.get('roll_no'),
        student_class=request.form.get('class'),
        phone=request.form.get('phone'),
        address=request.form.get('address')
    )
    db.session.add(new_s)
    db.session.commit()
    return redirect(url_for('dashboard', role='admin'))

@app.route('/submit_result', methods=['POST'])
def submit_result():
    if session.get('role') != 'admin':
        return "Admin only!", 403
    new_res = Result(
        roll_no=request.form.get('roll_no'),
        result_class=request.form.get('result_class'),
        exam_term=request.form.get('exam_term'),
        english=int(request.form.get('english') or 0),
        maths=int(request.form.get('maths') or 0),
        urdu=int(request.form.get('urdu') or 0),
        science=int(request.form.get('science') or 0),
        islamiat=int(request.form.get('islamiat') or 0),
        computer=int(request.form.get('computer') or 0),
        physics=int(request.form.get('physics') or 0),
        chemistry=int(request.form.get('chemistry') or 0),
        phy_lab=int(request.form.get('phy_lab') or 0),
        chem_lab=int(request.form.get('chem_lab') or 0),
        bio_lab=int(request.form.get('bio_lab') or 0),
        comp_lab=int(request.form.get('comp_lab') or 0),
    )
    db.session.add(new_res)
    db.session.commit()
    return redirect(url_for('view_result', result_id=new_res.id))

@app.route('/result/<int:result_id>')
def view_result(result_id):
    result = Result.query.get_or_404(result_id)
    student = Student.query.filter_by(roll_no=result.roll_no).first()
    role = session.get('role', 'admin')
    subject_marks = [result.english, result.maths, result.urdu, result.science,
                     result.islamiat, result.computer, result.physics, result.chemistry]
    total_marks = sum(subject_marks)
    max_marks = 800
    if result.result_class in ['9', '10']:
        lab_marks = [m for m in [result.phy_lab, result.chem_lab, result.bio_lab, result.comp_lab] if m > 0]
        total_marks += sum(lab_marks)
        max_marks += len(lab_marks) * 100
    percentage = round((total_marks / max_marks) * 100, 1) if max_marks > 0 else 0
    if percentage >= 80: overall_grade = 'A'
    elif percentage >= 65: overall_grade = 'B'
    elif percentage >= 50: overall_grade = 'C'
    else: overall_grade = 'F'
    passed = percentage >= 50
    now = datetime.now().strftime("%d %B %Y, %I:%M %p")
    return render_template('result.html', result=result, student=student, role=role,
                           total_marks=total_marks, max_marks=max_marks,
                           percentage=percentage, overall_grade=overall_grade,
                           passed=passed, now=now)

@app.route('/complaint', methods=['POST'])
def complaint():
    msg = request.form.get('feedback')
    if msg:
        db.session.add(Complaint(feedback=msg))
        db.session.commit()
    return redirect(url_for('dashboard', role=session.get('role', 'parent')))

@app.route('/schedule_ptm', methods=['POST'])
def schedule_ptm():
    if session.get('role') != 'admin':
        return "Access Denied", 403
    new_ptm = PTM(
        date=request.form.get('m_date'),
        time=request.form.get('m_time'),
        parent_info=request.form.get('p_info')
    )
    db.session.add(new_ptm)
    db.session.commit()
    return redirect(url_for('dashboard', role='admin'))

# --- ATTENDANCE ROUTE ---
@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    if session.get('role') != 'admin':
        return "Access Denied", 403
    roll_no = request.form.get('roll_no')
    att_date = request.form.get('att_date')
    status = request.form.get('status')
    student = Student.query.filter_by(roll_no=roll_no).first()

    # Same date same student ka duplicate check
    existing = Attendance.query.filter_by(roll_no=roll_no, date=att_date).first()
    if existing:
        existing.status = status  # Update kar dein
    else:
        new_att = Attendance(
            roll_no=roll_no,
            student_name=student.name if student else 'N/A',
            student_class=student.student_class if student else 'N/A',
            date=att_date,
            status=status
        )
        db.session.add(new_att)
    db.session.commit()
    return redirect(url_for('dashboard', role='admin'))

# --- DISCIPLINE ROUTE ---
@app.route('/add_discipline', methods=['POST'])
def add_discipline():
    if session.get('role') != 'admin':
        return "Access Denied", 403
    roll_no = request.form.get('roll_no')
    month = request.form.get('month')
    score = int(request.form.get('score') or 0)
    student = Student.query.filter_by(roll_no=roll_no).first()

    # Same month same student ka duplicate check
    existing = Discipline.query.filter_by(roll_no=roll_no, month=month).first()
    if existing:
        existing.score = score  # Update kar dein
    else:
        new_disc = Discipline(
            roll_no=roll_no,
            student_name=student.name if student else 'N/A',
            student_class=student.student_class if student else 'N/A',
            month=month,
            score=score
        )
        db.session.add(new_disc)
    db.session.commit()
    return redirect(url_for('dashboard', role='admin'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)