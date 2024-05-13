# Project Structure

# FlaSQL Project Structure

The FlaSQL project is organized as follows:

### Root Directory: FlaSQL
- **app/** - Contains the core application code and resources.
  - **static/** - Holds static files like CSS, JavaScript, and images.
  - **templates/** - Contains HTML templates for the application.
    - **private/** - Templates accessible only to authenticated users.
      - `dashboard.html` - Main dashboard view for logged-in users.
      - `dashboardTest.html` - Test version of the dashboard.
      - `private_base.html` - Base HTML template for private pages.
      - `private_baseTest.html` - Test version of the private base template.
    - **public/** - Templates for public-facing pages.
      - `404.html` - Custom 404 error page.
      - `about.html` - Information about the application.
      - `base.html` - Base HTML template for public pages.
      - `landing.html` - Landing page of the website.
      - `login.html` - User login form.
      - `register.html` - User registration form.
  - **utils/** - Utility scripts and modules to support the application.
    - `dbInfo.py` - Contains functions to handle database interactions.
  - `forms.py` - Defines web forms for registration and login.
  - `models.py` - Data models for the application.
  - `routes.py` - URL routes and their corresponding view functions.
  - `__init__.py` - Initializes the Flask application.

- **instance/** - Instance-specific configuration and files.
- **migrations/** - Database migration scripts.
- `.gitignore` - Specifies intentionally untracked files to ignore.
- `config.py` - General configuration settings for the application.
- `ProjectStructure.md` - Markdown file describing the project structure.
- `README.md` - README file with installation and usage instructions.
- `requirements.txt` - Specifies the Python dependencies of the project.
- `run.py` - The entry point to start the application.

