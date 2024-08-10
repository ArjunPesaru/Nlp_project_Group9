

---
## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before running the application, ensure you have the following installed:

- **Python 3.x**
- **PostgreSQL** - A powerful, open-source object-relational database system.
- **psycopg2** - PostgreSQL adapter for Python.

## Installation

### Step 1: Clone the Repository

```bash
git clone [(https://github.com/ArjunPesaru/Nlp_project_Group9)

```

### Step 2: Set Up a Virtual Environment

It's a good practice to use a virtual environment to manage dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Step 3: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Step 4: Install PostgreSQL

If you haven't installed PostgreSQL yet, you can install it by following the official documentation: [PostgreSQL Download](https://www.postgresql.org/download/).

### Step 5: Install Psycopg2

Psycopg2 is required to connect Python with PostgreSQL:

```bash
pip install psycopg2
```

## Database Setup

### Step 1: Create a PostgreSQL Database

First, log in to PostgreSQL and create a new database:

```sql
CREATE DATABASE taskscheduler;
```

### Step 2: Set Up a Database User (Optional)

You can create a specific user for this database:

```sql
CREATE USER taskuser WITH ENCRYPTED PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE taskscheduler TO taskuser;
```

### Step 3: Run Migrations (if applicable)

If your project uses migrations for setting up the database schema, apply them using:

```bash
python manage.py migrate  # If you are using Django
```

## Configuration

Update the application's configuration to use PostgreSQL. This might involve setting up environment variables or directly modifying a configuration file.

For example, in a Django project, modify `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'taskscheduler',
        'USER': 'taskuser',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

If using Flask or another framework, adjust the connection string accordingly:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://taskuser:password@localhost/taskscheduler'
```

## Usage

To run the task scheduling service, use the following command:

```bash
python main.py
```

The service will process a set of tasks and calculate the minimum number of machines required to complete them.

## Testing

To run the tests, use the following command:

```bash
python -m unittest discover tests
```

This will execute the test cases in the `tests` directory to ensure the functionality of the service.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This README provides a comprehensive guide to setting up and running the task scheduling service using PostgreSQL instead of XAMPP. If you need to make additional changes based on your specific setup, feel free to modify the content accordingly.
