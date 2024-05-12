# Project Structure

```bash

FlaSQL/
│
├── app/
│   ├── __init__.py       # Initializes the Flask app and imports other components
│   ├── models.py         # Defines database models, including User
│   ├── forms.py          # Defines forms for user registration and login
│   ├── routes.py         # Handles all the routes for the application
│   ├── templates/        # HTML files for the application
│   │   ├── base.html     # Base template with common layout and links to Tailwind CSS
│   │   ├── index.html    # Main dashboard page after login
│   │   ├── login.html    # Login page template
│   │   ├── register.html # Registration page template
│   │   └── logout.html   # Logout confirmation page
│   └── static/
│       └── css/          # Folder for CSS files (if any additional styles are needed)
│
├── config.py             # Contains configuration for the application
├── run.py                # Entry point to run the Flask application
└── requirements.txt      # List of dependencies



```