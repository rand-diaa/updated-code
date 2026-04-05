# Online Examination System 🎓

## What the System Is

This is a comprehensively featured Django-based Online Examination System. It provides three separate portals:

1. **Admin Panel**: For staff members to manage teachers, students, exam courses, and track overall scores. They also define exam schedules or manually start and stop live exam sessions.
2. **Teacher Portal**: Allows teachers to register, securely create exams/questions subject-by-subject, verify results, and monitor students.
3. **Student Portal**: Provides an accessible dashboard for students to view their subjects, start available active exams (Multiple Choice / True-False), and review their academic standing and grades.

The application is built primarily using Python and Django.

## How to Run It

To run this application locally, ensure you are in the root directory (`updated-code`) and follow these steps:

1. **Activate the Virtual Environment**:

   ```bash
   source .venv/bin/activate
   ```

2. **Install the Requirements**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run Database Migrations (If setting up fresh)**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```
   _The system is now accessible in your browser at `http://127.0.0.1:8000/`_

## Seeded Admin Credentials

For immediate administrative access to the platform (valuable for approving teacher signups and managing exams), an admin account has been seeded into the database.

Go to the **Admin Login** page (`http://127.0.0.1:8000/adminlogin`) and use the following credentials:

- **Username**: `admin`
- **Password**: `admin123`
