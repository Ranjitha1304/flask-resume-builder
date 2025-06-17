from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import pdfkit
import os
from xhtml2pdf import pisa

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resumes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    education = db.Column(db.Text)
    experience = db.Column(db.Text)
    skills = db.Column(db.Text)

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form
    resume = Resume(
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        address=data['address'],
        education=data['education'],
        experience=data['experience'],
        skills=data['skills']
    )
    db.session.add(resume)
    db.session.commit()
    return redirect(url_for('resume', resume_id=resume.id))

@app.route('/resume/<int:resume_id>')
def resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    return render_template('resume.html', resume=resume)

@app.route('/download/<int:resume_id>')
def download(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    rendered = render_template('resume.html', resume=resume)
    pdf_path = f"generated/resume_{resume.id}.pdf"
    with open(pdf_path, "w+b") as f:
        pisa_status = pisa.CreatePDF(rendered, dest=f)
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists('generated'):
        os.makedirs('generated')
    with app.app_context():
        db.create_all()
    app.run(debug=True)
