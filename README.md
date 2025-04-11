# MoneyMate - Personal Finance Tracker

A web-based personal finance management system that helps users track their expenses, income, and manage their budget effectively.

## Features

- Transaction Management (Income & Expenses)
- Category-based Expense Tracking
- Statistical Analysis with Charts
- Bill Splitter
- User Profile Management

## Setup Instructions

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```
     source venv/bin/activate
     ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure

```
DBMS project/
├── static/          # CSS and static files
├── templates/       # HTML templates
├── app.py          # Main application file
├── requirements.txt # Project dependencies
└── README.md       # This file
```

## Technologies Used

- Flask (Python web framework)
- SQLAlchemy (Database ORM)
- HTML/CSS
- JavaScript
- SQLite (Database) 