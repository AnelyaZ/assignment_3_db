from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

import os

app = Flask(__name__)

db_url = os.getenv("DATABASE_URL", "")

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "USER"

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    given_name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(25))
    profile_description = db.Column(db.Text)
    password = db.Column(db.String(255), nullable=False)


class Caregiver(db.Model):
    __tablename__ = "caregiver"

    caregiver_user_id = db.Column(db.Integer, db.ForeignKey("USER.user_id"), primary_key=True)
    photo = db.Column(db.String(255))
    gender = db.Column(db.String(10))
    caregiving_type = db.Column(db.String(50), nullable=False)
    hourly_rate = db.Column(db.Numeric(10, 3))

    user = db.relationship("User", backref="caregiver_profile")


class Member(db.Model):
    __tablename__ = "member"

    member_user_id = db.Column(db.Integer, db.ForeignKey("USER.user_id"), primary_key=True)
    house_rules = db.Column(db.Text, nullable=False)
    dependent_description = db.Column(db.Text, nullable=False)

    user = db.relationship("User", backref="member_profile")


class Address(db.Model):
    __tablename__ = "address"

    member_user_id = db.Column(db.Integer, db.ForeignKey("member.member_user_id"), primary_key=True)
    house_number = db.Column(db.String(25), nullable=False)
    street = db.Column(db.String(150), nullable=False)
    town = db.Column(db.String(100), nullable=False)

    member = db.relationship("Member", backref="address")


class Job(db.Model):
    __tablename__ = "job"

    job_id = db.Column(db.Integer, primary_key=True)
    member_user_id = db.Column(db.Integer, db.ForeignKey("member.member_user_id"), nullable=False)
    required_caregiving_type = db.Column(db.String(50), nullable=False)
    other_requirements = db.Column(db.Text)
    date_posted = db.Column(db.Date, nullable=False)

    member = db.relationship("Member", backref="jobs")


class JobApplication(db.Model):
    __tablename__ = "job_application"

    caregiver_user_id = db.Column(db.Integer, db.ForeignKey("caregiver.caregiver_user_id"), primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.job_id"), primary_key=True)
    date_applied = db.Column(db.Date, nullable=False)

    caregiver = db.relationship("Caregiver", backref="job_applications")
    job = db.relationship("Job", backref="applications")


class Appointment(db.Model):
    __tablename__ = "appointment"

    appointment_id = db.Column(db.Integer, primary_key=True)
    caregiver_user_id = db.Column(db.Integer, db.ForeignKey("caregiver.caregiver_user_id"), nullable=False)
    member_user_id = db.Column(db.Integer, db.ForeignKey("member.member_user_id"), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    work_hours = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(25), nullable=False)

    caregiver = db.relationship("Caregiver", backref="appointments")
    member = db.relationship("Member", backref="appointments")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/users")
def list_users():
    users = User.query.all()
    return render_template("users_list.html", users=users)


@app.route("/users/new", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        max_id = db.session.query(func.max(User.user_id)).scalar()
        if max_id is None:
            max_id = 0
        new_id = max_id + 1
        user = User(
            user_id=new_id,
            email=request.form["email"],
            given_name=request.form["given_name"],
            surname=request.form["surname"],
            city=request.form["city"],
            phone_number=request.form.get("phone_number"),
            profile_description=request.form.get("profile_description"),
            password=request.form["password"],
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("list_users"))
    return render_template("user_form.html", user=None, form_action=url_for("create_user"))


@app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        user.email = request.form["email"]
        user.given_name = request.form["given_name"]
        user.surname = request.form["surname"]
        user.city = request.form["city"]
        user.phone_number = request.form.get("phone_number")
        user.profile_description = request.form.get("profile_description")
        user.password = request.form["password"]
        db.session.commit()
        return redirect(url_for("list_users"))
    return render_template("user_form.html", user=user, form_action=url_for("edit_user", user_id=user_id))


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("list_users"))


@app.route("/caregivers")
def list_caregivers():
    caregivers = Caregiver.query.all()
    return render_template("caregiver_list.html", caregivers=caregivers)


@app.route("/caregivers/new", methods=["GET", "POST"])
def create_caregiver():
    if request.method == "POST":
        caregiver_user_id = int(request.form["caregiver_user_id"])
        if not User.query.get(caregiver_user_id):
            return "Error: User does not exist"
        if Caregiver.query.get(caregiver_user_id):
            return "Error: This user is already a caregiver"
        caregiver = Caregiver(
            caregiver_user_id=caregiver_user_id,
            photo=request.form.get("photo"),
            gender=request.form.get("gender"),
            caregiving_type=request.form["caregiving_type"],
            hourly_rate=request.form.get("hourly_rate"),
        )
        db.session.add(caregiver)
        db.session.commit()
        return redirect(url_for("list_caregivers"))
    users = User.query.all()
    return render_template("caregiver_form.html", caregiver=None, users=users, form_action=url_for("create_caregiver"))


@app.route("/caregivers/<int:caregiver_user_id>/edit", methods=["GET", "POST"])
def edit_caregiver(caregiver_user_id):
    caregiver = Caregiver.query.get_or_404(caregiver_user_id)
    if request.method == "POST":
        caregiver.photo = request.form.get("photo")
        caregiver.gender = request.form.get("gender")
        caregiver.caregiving_type = request.form["caregiving_type"]
        caregiver.hourly_rate = request.form.get("hourly_rate")
        db.session.commit()
        return redirect(url_for("list_caregivers"))
    return render_template("caregiver_form.html", caregiver=caregiver, users=None, form_action=url_for("edit_caregiver", caregiver_user_id=caregiver_user_id))


@app.route("/caregivers/<int:caregiver_user_id>/delete", methods=["POST"])
def delete_caregiver(caregiver_user_id):
    caregiver = Caregiver.query.get_or_404(caregiver_user_id)
    db.session.delete(caregiver)
    db.session.commit()
    return redirect(url_for("list_caregivers"))


@app.route("/members")
def list_members():
    members = Member.query.all()
    return render_template("member_list.html", members=members)


@app.route("/members/new", methods=["GET", "POST"])
def create_member():
    if request.method == "POST":
        member_user_id = int(request.form["member_user_id"])
        if not User.query.get(member_user_id):
            return "Error: User does not exist"
        if Member.query.get(member_user_id):
            return "Error: This user is already a member"
        member = Member(
            member_user_id=member_user_id,
            house_rules=request.form["house_rules"],
            dependent_description=request.form["dependent_description"],
        )
        db.session.add(member)
        db.session.commit()
        return redirect(url_for("list_members"))
    users = User.query.all()
    return render_template("member_form.html", member=None, users=users, form_action=url_for("create_member"))


@app.route("/members/<int:member_user_id>/edit", methods=["GET", "POST"])
def edit_member(member_user_id):
    member = Member.query.get_or_404(member_user_id)
    if request.method == "POST":
        member.house_rules = request.form["house_rules"]
        member.dependent_description = request.form["dependent_description"]
        db.session.commit()
        return redirect(url_for("list_members"))
    return render_template("member_form.html", member=member, users=None, form_action=url_for("edit_member", member_user_id=member_user_id))


@app.route("/members/<int:member_user_id>/delete", methods=["POST"])
def delete_member(member_user_id):
    member = Member.query.get_or_404(member_user_id)
    db.session.delete(member)
    db.session.commit()
    return redirect(url_for("list_members"))


@app.route("/addresses")
def list_addresses():
    addresses = Address.query.all()
    return render_template("address_list.html", addresses=addresses)


@app.route("/addresses/new", methods=["GET", "POST"])
def create_address():
    if request.method == "POST":
        member_user_id = int(request.form["member_user_id"])
        if not Member.query.get(member_user_id):
            return "Error: Member does not exist"
        if Address.query.get(member_user_id):
            return "Error: This member already has an address"
        address = Address(
            member_user_id=member_user_id,
            house_number=request.form["house_number"],
            street=request.form["street"],
            town=request.form["town"],
        )
        db.session.add(address)
        db.session.commit()
        return redirect(url_for("list_addresses"))
    members = Member.query.all()
    return render_template("address_form.html", address=None, members=members, form_action=url_for("create_address"))


@app.route("/addresses/<int:member_user_id>/edit", methods=["GET", "POST"])
def edit_address(member_user_id):
    address = Address.query.get_or_404(member_user_id)
    if request.method == "POST":
        address.house_number = request.form["house_number"]
        address.street = request.form["street"]
        address.town = request.form["town"]
        db.session.commit()
        return redirect(url_for("list_addresses"))
    members = Member.query.all()
    return render_template("address_form.html", address=address, members=members, form_action=url_for("edit_address", member_user_id=member_user_id))


@app.route("/addresses/<int:member_user_id>/delete", methods=["POST"])
def delete_address(member_user_id):
    address = Address.query.get_or_404(member_user_id)
    db.session.delete(address)
    db.session.commit()
    return redirect(url_for("list_addresses"))


@app.route("/jobs")
def list_jobs():
    jobs = Job.query.all()
    return render_template("job_list.html", jobs=jobs)


@app.route("/jobs/new", methods=["GET", "POST"])
def create_job():
    if request.method == "POST":
        max_id = db.session.query(func.max(Job.job_id)).scalar()
        if max_id is None:
            max_id = 0
        new_id = max_id + 1
        member_user_id = int(request.form["member_user_id"])
        if not Member.query.get(member_user_id):
            return "Error: Member does not exist"
        job = Job(
            job_id=new_id,
            member_user_id=member_user_id,
            required_caregiving_type=request.form["required_caregiving_type"],
            other_requirements=request.form.get("other_requirements"),
            date_posted=func.current_date(),
        )
        db.session.add(job)
        db.session.commit()
        return redirect(url_for("list_jobs"))
    members = Member.query.all()
    return render_template("job_form.html", job=None, members=members, form_action=url_for("create_job"))


@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    if request.method == "POST":
        member_user_id = int(request.form["member_user_id"])
        if not Member.query.get(member_user_id):
            return "Error: Member does not exist"
        job.member_user_id = member_user_id
        job.required_caregiving_type = request.form["required_caregiving_type"]
        job.other_requirements = request.form.get("other_requirements")
        db.session.commit()
        return redirect(url_for("list_jobs"))
    members = Member.query.all()
    return render_template("job_form.html", job=job, members=members, form_action=url_for("edit_job", job_id=job_id))


@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return redirect(url_for("list_jobs"))


@app.route("/job_applications")
def list_job_applications():
    job_apps = JobApplication.query.all()
    return render_template("job_application_list.html", job_apps=job_apps)


@app.route("/job_applications/new", methods=["GET", "POST"])
def create_job_application():
    if request.method == "POST":
        caregiver_user_id = int(request.form["caregiver_user_id"])
        job_id = int(request.form["job_id"])
        if not Caregiver.query.get(caregiver_user_id):
            return "Error: Caregiver does not exist"
        if not Job.query.get(job_id):
            return "Error: Job does not exist"
        if JobApplication.query.get((caregiver_user_id, job_id)):
            return "Error: This job application already exists"
        job_app = JobApplication(
            caregiver_user_id=caregiver_user_id,
            job_id=job_id,
            date_applied=func.current_date(),
        )
        db.session.add(job_app)
        db.session.commit()
        return redirect(url_for("list_job_applications"))
    caregivers = Caregiver.query.all()
    jobs = Job.query.all()
    return render_template("job_application_form.html", job_app=None, caregivers=caregivers, jobs=jobs, form_action=url_for("create_job_application"))


@app.route("/job_applications/<int:caregiver_user_id>/<int:job_id>/edit", methods=["GET", "POST"])
def edit_job_application(caregiver_user_id, job_id):
    job_app = JobApplication.query.get_or_404((caregiver_user_id, job_id))
    if request.method == "POST":
        new_caregiver_user_id = int(request.form["caregiver_user_id"])
        new_job_id = int(request.form["job_id"])
        if not Caregiver.query.get(new_caregiver_user_id):
            return "Error: Caregiver does not exist"
        if not Job.query.get(new_job_id):
            return "Error: Job does not exist"
        if (new_caregiver_user_id, new_job_id) != (caregiver_user_id, job_id) and JobApplication.query.get((new_caregiver_user_id, new_job_id)):
            return "Error: This job application already exists"
        db.session.delete(job_app)
        new_app = JobApplication(
            caregiver_user_id=new_caregiver_user_id,
            job_id=new_job_id,
            date_applied=job_app.date_applied,
        )
        db.session.add(new_app)
        db.session.commit()
        return redirect(url_for("list_job_applications"))
    caregivers = Caregiver.query.all()
    jobs = Job.query.all()
    return render_template("job_application_form.html", job_app=job_app, caregivers=caregivers, jobs=jobs, form_action=url_for("edit_job_application", caregiver_user_id=caregiver_user_id, job_id=job_id))


@app.route("/job_applications/<int:caregiver_user_id>/<int:job_id>/delete", methods=["POST"])
def delete_job_application(caregiver_user_id, job_id):
    job_app = JobApplication.query.get_or_404((caregiver_user_id, job_id))
    db.session.delete(job_app)
    db.session.commit()
    return redirect(url_for("list_job_applications"))


@app.route("/appointments")
def list_appointments():
    appointments = Appointment.query.all()
    return render_template("appointment_list.html", appointments=appointments)


@app.route("/appointments/new", methods=["GET", "POST"])
def create_appointment():
    if request.method == "POST":
        max_id = db.session.query(func.max(Appointment.appointment_id)).scalar()
        if max_id is None:
            max_id = 0
        new_id = max_id + 1
        caregiver_user_id = int(request.form["caregiver_user_id"])
        member_user_id = int(request.form["member_user_id"])
        if not Caregiver.query.get(caregiver_user_id):
            return "Error: Caregiver does not exist"
        if not Member.query.get(member_user_id):
            return "Error: Member does not exist"
        appointment = Appointment(
            appointment_id=new_id,
            caregiver_user_id=caregiver_user_id,
            member_user_id=member_user_id,
            appointment_date=request.form["appointment_date"],
            appointment_time=request.form["appointment_time"],
            work_hours=int(request.form["work_hours"]),
            status=request.form["status"],
        )
        db.session.add(appointment)
        db.session.commit()
        return redirect(url_for("list_appointments"))
    caregivers = Caregiver.query.all()
    members = Member.query.all()
    return render_template("appointment_form.html", appointment=None, caregivers=caregivers, members=members, form_action=url_for("create_appointment"))


@app.route("/appointments/<int:appointment_id>/edit", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if request.method == "POST":
        caregiver_user_id = int(request.form["caregiver_user_id"])
        member_user_id = int(request.form["member_user_id"])
        if not Caregiver.query.get(caregiver_user_id):
            return "Error: Caregiver does not exist"
        if not Member.query.get(member_user_id):
            return "Error: Member does not exist"
        appointment.caregiver_user_id = caregiver_user_id
        appointment.member_user_id = member_user_id
        appointment.appointment_date = request.form["appointment_date"]
        appointment.appointment_time = request.form["appointment_time"]
        appointment.work_hours = int(request.form["work_hours"])
        appointment.status = request.form["status"]
        db.session.commit()
        return redirect(url_for("list_appointments"))
    caregivers = Caregiver.query.all()
    members = Member.query.all()
    return render_template("appointment_form.html", appointment=appointment, caregivers=caregivers, members=members, form_action=url_for("edit_appointment", appointment_id=appointment_id))


@app.route("/appointments/<int:appointment_id>/delete", methods=["POST"])
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for("list_appointments"))


if __name__ == "__main__":
    app.run(debug=True)
