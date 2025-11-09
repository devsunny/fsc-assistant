import os
import zipfile

from ..base import CodeGenerator


class WebProjectInitGenerator(CodeGenerator):
    """
    A class to generate a Flask project directory structure with backend (Flask,
    Flask-Restx, Pydantic, PostgreSQL) and frontend (Vue 3, Vuetify) support.
    """

    def _generate_flask_backend_files(self, base_path):
        """
        Generates backend (Flask) specific files and directories.

        Args:
            base_path (str): The base path for the backend directory.
        """
        print(base_path)
        backend_app_path = os.path.join(base_path, "app")
        backend_api_path = os.path.join(backend_app_path, "api")
        backend_dao_path = os.path.join(backend_app_path, "dao")
        backend_schemas_path = os.path.join(backend_app_path, "schemas")
        backend_utils_path = os.path.join(backend_app_path, "utils")
        backend_tests_path = os.path.join(base_path, "tests")  # New tests directory

        # Create backend directories
        self._create_directory(backend_dao_path)
        self._create_directory(backend_api_path)
        self._create_directory(backend_app_path)
        self._create_directory(backend_schemas_path)
        self._create_directory(backend_utils_path)
        self._create_directory(backend_tests_path)  # Create tests directory

        # Create backend files
        self._create_file(
            os.path.join(backend_app_path, "__init__.py"),
            content="""
from flask import Flask
from flask_restx import Api
from .config import Config
from .database import db
import logging.config # Import logging.config for dictConfig
import yaml # Import yaml to load config
import os # For path joining

# Setup logging before app creation
def setup_logging():
    config_path = os.path.join(os.path.dirname(__file__), 'logging_config.yaml')
    with open(config_path, 'rt') as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

setup_logging()
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    api = Api(
        app,
        version='1.0',
        title='Flask-Vue API',
        description='A REST API for the Flask-Vue project',
        doc='/docs'
    )

    from .api.resources import api_bp
    api.add_namespace(api_bp, path='/api')

    with app.app_context():
        # Import models to ensure they are known to SQLAlchemy before create_all()
        from .schemas import user # Import the user model from the new schemas directory
        db.create_all() # Create database tables if they don't exist
        logger.info("Database tables checked/created.")

    logger.info("Flask application created and configured.")
    return app
""",
        )

        self._create_file(
            os.path.join(backend_app_path, "config.py"),
            content="""
import os

class Config:
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a_very_secret_key_for_development')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/mydatabase'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESTX_MASK_SWAGGER = False # To show all fields in Swagger UI
""",
        )

        self._create_file(
            os.path.join(backend_app_path, "database.py"),
            content='''
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import os

db = SQLAlchemy()

def get_connection():
    """
    Establishes and returns a direct psycopg2 connection to the PostgreSQL database.
    This can be used for raw ANSI SQL queries that bypass SQLAlchemy's ORM.
    """
    db_url = os.environ.get(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/mydatabase'
    )
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"Error connecting to database with psycopg2: {e}")
        raise
''',
        )

        self._create_file(
            os.path.join(backend_app_path, "main.py"),
            content="""
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Default to 0.0.0.0 for Docker compatibility
    host = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    app.run(host=host, port=port)
""",
        )

        self._create_file(
            os.path.join(backend_api_path, "__init__.py"),
            content="""
from flask_restx import Namespace

api_bp = Namespace('api', description='API operations')
""",
        )

        self._create_file(
            os.path.join(backend_dao_path, "__init__.py"),
            content='''
""" module contains raw SQL access to underline database """"

''',
        )

        self._create_file(
            os.path.join(backend_api_path, "resources.py"),
            content="""
from flask import request
from flask_restx import Resource, fields
from pydantic import BaseModel
from .__init__ import api_bp
from ..database import db, get_connection # Import get_connection
import psycopg2.extras # For DictCursor

from ..schemas.user import User as DBUser # Alias to avoid name conflict with Pydantic User, and updated path

# Pydantic model for request validation and response serialization
class UserSchema(BaseModel):
    id: int | None = None
    username: str
    email: str

    class Config:
        from_attributes = True # Allow Pydantic to create model from ORM object

user_model = api_bp.model('User', {
    'id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'username': fields.String(required=True, description='The user username'),
    'email': fields.String(required=True, description='The user email address')
})

@api_bp.route('/users')
class UserList(Resource):
    @api_bp.doc('list_users')
    @api_bp.marshal_list_with(user_model)
    def get(self):
        '''List all users'''
        users = DBUser.query.all()
        return [UserSchema.model_validate(user).model_dump() for user in users]

    @api_bp.doc('create_user')
    @api_bp.expect(user_model)
    @api_bp.marshal_with(user_model, code=201)
    def post(self):
        '''Create a new user'''
        try:
            user_data = UserSchema(**api_bp.payload)
            new_user = DBUser(username=user_data.username, email=user_data.email)
            db.session.add(new_user)
            db.session.commit()
            return UserSchema.model_validate(new_user).model_dump(), 201
        except Exception as e:
            api_bp.abort(400, f"Error creating user: {e}")

@api_bp.route('/users/<int:id>')
@api_bp.param('id', 'The user identifier')
@api_bp.response(404, 'User not found')
class User(Resource):
    @api_bp.doc('get_user')
    @api_bp.marshal_with(user_model)
    def get(self, id):
        '''Fetch a user given its identifier'''
        user = DBUser.query.get_or_404(id)
        return UserSchema.model_validate(user).model_dump()

    @api_bp.doc('update_user')
    @api_bp.expect(user_model)
    @api_bp.marshal_with(user_model)
    def put(self, id):
        '''Update a user given its identifier'''
        user = DBUser.query.get_or_404(id)
        try:
            user_data = UserSchema(**api_bp.payload)
            user.username = user_data.username
            user.email = user_data.email
            db.session.commit()
            return UserSchema.model_validate(user).model_dump()
        except Exception as e:
            api_bp.abort(400, f"Error updating user: {e}")

    @api_bp.doc('delete_user')
    @api_bp.response(204, 'User deleted')
    def delete(self, id):
        '''Delete a user given its identifier'''
        user = DBUser.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return '', 204

@api_bp.route('/raw-sql/users-sqlalchemy')
class RawSqlUserListSQLAlchemy(Resource):
    @api_bp.doc('list_users_raw_sql_sqlalchemy')
    @api_bp.marshal_list_with(user_model)
    def get(self):
        '''List all users using raw SQL via SQLAlchemy session'''
        try:
            # Example of executing a raw SQL query using SQLAlchemy's session
            result = db.session.execute(db.text("SELECT id, username, email FROM users")).fetchall()
            # Convert SQLAlchemy Row objects to dictionary for Pydantic validation
            users_data = [{'id': row.id, 'username': row.username, 'email': row.email} for row in result]
            return [UserSchema.model_validate(user_data).model_dump() for user_data in users_data]
        except Exception as e:
            api_bp.abort(500, f"Error fetching users with raw SQL (SQLAlchemy): {e}")

@api_bp.route('/raw-sql/add-user-sqlalchemy')
class RawSqlAddUserSQLAlchemy(Resource):
    @api_bp.doc('add_user_raw_sql_sqlalchemy')
    @api_bp.expect(user_model)
    @api_bp.marshal_with(user_model, code=201)
    def post(self):
        '''Add a new user using raw SQL via SQLAlchemy session'''
        try:
            user_data = UserSchema(**api_bp.payload)
            # Example of executing an INSERT statement with raw SQL via SQLAlchemy
            # IMPORTANT: Always use text() and bindparams for parameterized queries to prevent SQL Injection!
            insert_sql = db.text("INSERT INTO users (username, email) VALUES (:username, :email) RETURNING id, username, email")
            result = db.session.execute(
                insert_sql,
                {'username': user_data.username, 'email': user_data.email}
            ).fetchone()
            db.session.commit()

            if result:
                new_user_data = {'id': result.id, 'username': result.username, 'email': result.email}
                return UserSchema.model_validate(new_user_data).model_dump(), 201
            else:
                api_bp.abort(500, "Failed to retrieve new user data after raw SQL insert (SQLAlchemy).")
        except Exception as e:
            db.session.rollback() # Rollback in case of error
            api_bp.abort(400, f"Error adding user with raw SQL (SQLAlchemy): {e}")

@api_bp.route('/raw-sql/users-psycopg2')
class RawSqlUserListPsycopg2(Resource):
    @api_bp.doc('list_users_raw_sql_psycopg2')
    @api_bp.marshal_list_with(user_model)
    def get(self):
        '''List all users using raw SQL via psycopg2 direct connection'''
        conn = None
        try:
            conn = get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) # Use DictCursor for dictionary results
            cur.execute("SELECT id, username, email FROM users")
            users_data = cur.fetchall()
            cur.close()
            return [UserSchema.model_validate(dict(user)).model_dump() for user in users_data]
        except Exception as e:
            api_bp.abort(500, f"Error fetching users with raw SQL (psycopg2): {e}")
        finally:
            if conn:
                conn.close()

@api_bp.route('/raw-sql/add-user-psycopg2')
class RawSqlAddUserPsycopg2(Resource):
    @api_bp.doc('add_user_raw_sql_psycopg2')
    @api_bp.expect(user_model)
    @api_bp.marshal_with(user_model, code=201)
    def post(self):
        '''Add a new user using raw SQL via psycopg2 direct connection'''
        conn = None
        try:
            user_data = UserSchema(**api_bp.payload)
            conn = get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            # IMPORTANT: Use %s placeholders for psycopg2 to prevent SQL Injection!
            cur.execute(
                "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING id, username, email",
                (user_data.username, user_data.email)
            )
            result = cur.fetchone()
            conn.commit() # Commit changes for psycopg2
            cur.close()

            if result:
                return UserSchema.model_validate(dict(result)).model_dump(), 201
            else:
                api_bp.abort(500, "Failed to retrieve new user data after raw SQL insert (psycopg2).")
        except Exception as e:
            if conn:
                conn.rollback() # Rollback in case of error
            api_bp.abort(400, f"Error adding user with raw SQL (psycopg2): {e}")
        finally:
            if conn:
                conn.close()
""",
        )

        self._create_file(
            os.path.join(backend_schemas_path, "__init__.py"),
            content="""
from .user import User
""",
        )
        self._create_file(
            os.path.join(backend_schemas_path, "base.py"),
            content="""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
""",
        )

        self._create_file(
            os.path.join(backend_schemas_path, "user.py"),
            content="""
from .base import Base


class User(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
""",
        )

        self._create_file(os.path.join(backend_utils_path, "__init__.py"), content="")

        # Changed to logging_config.yaml
        self._create_file(
            os.path.join(backend_app_path, "logging_config.yaml"),
            content="""
version: 1
formatters:
  simple:
    format: '%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: simple
    stream: ext://sys.stdout
loggers:
  # Root logger
  '':
    handlers: [console]
    level: INFO
    propagate: yes
  # Specific loggers
  sqlalchemy.engine:
    level: WARNING
  werkzeug:
    level: WARNING
""",
        )

        self._create_file(
            os.path.join(base_path, "requirements.txt"),
            content="""
Flask==3.1.1
Flask-RESTx==1.3.0
Flask-SQLAlchemy==3.1.1
psycopg2-binary==2.9.10
pydantic==2.5.3
python-dotenv==1.1.1
gunicorn==23.0.0
PyYAML==6.0.2 # Added for YAML logging configuration
atlas-web-base>=0.0.147
atlas-shared-library>=0.0.84
""",
        )
        # install_requirements(os.path.join(base_path, "requirements.txt"))

        self._create_file(
            os.path.join(base_path, "pytest.ini"),
            content="""
[pytest]
pythonpath = app
testpaths = tests
""",
        )

        # Create example test file
        self._create_file(
            os.path.join(backend_tests_path, "test_api.py"),
            content='''
import pytest
from app import create_app
from app.database import db
from app.schemas.user import User

@pytest.fixture(scope='module')
def app():
    """
    Fixture to create and configure a Flask app for testing.
    Uses an in-memory SQLite database for fast tests.
    """
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # Use in-memory SQLite for tests
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with app.app_context():
        db.create_all() # Create tables for the test database
        yield app
        db.drop_all() # Drop tables after tests

@pytest.fixture(scope='module')
def client(app):
    """
    Fixture to provide a test client for the Flask app.
    """
    return app.test_client()

@pytest.fixture(scope='function')
def init_database(app):
    """
    Fixture to clear and initialize the database for each test function.
    """
    with app.app_context():
        # Clear existing data
        User.query.delete()
        db.session.commit()

        # Add some initial data
        user1 = User(username='testuser1', email='test1@example.com')
        user2 = User(username='testuser2', email='test2@example.com')
        db.session.add_all([user1, user2])
        db.session.commit()
        yield # Allow test to run
        User.query.delete() # Clean up after test
        db.session.commit()

def test_get_users(client, init_database):
    """
    Test the GET /api/users endpoint.
    """
    response = client.get('/api/users')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['username'] == 'testuser1'
    assert data[1]['email'] == 'test2@example.com'

def test_create_user(client, app):
    """
    Test the POST /api/users endpoint.
    """
    new_user_data = {
        'username': 'newuser',
        'email': 'newuser@example.com'
    }
    response = client.post('/api/users', json=new_user_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['username'] == 'newuser'
    assert data['email'] == 'newuser@example.com'

    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'

def test_get_single_user(client, init_database):
    """
    Test the GET /api/users/<id> endpoint.
    """
    with client.application.app_context():
        user = User.query.filter_by(username='testuser1').first()
        user_id = user.id

    response = client.get(f'/api/users/{user_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == 'testuser1'

def test_delete_user(client, app, init_database):
    """
    Test the DELETE /api/users/<id> endpoint.
    """
    with client.application.app_context():
        user = User.query.filter_by(username='testuser1').first()
        user_id = user.id

    response = client.delete(f'/api/users/{user_id}')
    assert response.status_code == 204

    with app.app_context():
        deleted_user = User.query.get(user_id)
        assert deleted_user is None
''',
        )

    def generate_flask_backend_project(self):
        project_root = self.output_dir
        self._create_directory(project_root)
        backend_path = os.path.join(project_root, "backend")
        self._create_directory(backend_path)
        print(f"Generating backend project in: {backend_path}")
        self._generate_flask_backend_files(backend_path)

    def generate_vue_frontend_project(self):
        project_root = self.output_dir
        self._create_directory(project_root)
        frontend_path = os.path.join(project_root, "frontend")
        self._create_directory(frontend_path)
        code_base = os.path.dirname(__file__)
        template_path = os.path.join(code_base, "resources", "mantis_templates.zip")

        try:
            # Open the zip file in read mode
            with zipfile.ZipFile(template_path, "r") as zip_ref:
                # Extract all contents to the specified directory
                zip_ref.extractall(frontend_path)
            print(f"Successfully extracted '{template_path}' to '{frontend_path}'")
        except zipfile.BadZipFile:
            print(f"Error: '{template_path}' is not a valid zip file.")
        except FileNotFoundError:
            print(f"Error: Zip file '{template_path}' not found.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def generate_project(self):
        """
        Generates the complete project directory structure and files.
        """
        project_root = self.output_dir
        self._create_directory(project_root)
        # Create root level files
        self._create_file(
            os.path.join(project_root, ".gitignore"),
            content="""
# Python
__pycache__/
*.pyc
.env
.venv/
.pytest_cache/

# Node.js
node_modules/
dist/
.env.local
.DS_Store
npm-debug.log*
yarn-debug.log*
yarn-error.log*
""",
        )

        self._create_file(
            os.path.join(project_root, "README.md"),
            content="""
# My Flask-Vue Full-Stack Project

This project is a boilerplate for a full-stack application using:

## Backend (Python/Flask)
- **Flask**: Web framework
- **Flask-RESTx**: For building REST APIs with Swagger UI
- **Pydantic**: For data validation and serialization
- **Flask-SQLAlchemy**: ORM for database interactions
- **psycopg2-binary**: PostgreSQL adapter
- **pytest**: For testing
- **Raw SQL Examples**: Demonstrates direct database interaction using `db.session.execute()` and `psycopg2` direct connections.
- **YAML Logging**: Configures application logging using a YAML file.

## Frontend (JavaScript/Vue)
- **Vue 3**: Progressive JavaScript framework
- **Vuetify 3**: Vue UI Library based on Material Design
- **Vite**: Frontend tooling for fast development

## Getting Started

### 1. Backend Setup

Navigate to the `backend` directory:
```bash
cd backend
```

Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

Install backend dependencies:
```bash
pip install -r requirements.txt
```

Set up your PostgreSQL database and update the `SQLALCHEMY_DATABASE_URI` in `backend/app/config.py` or via environment variables. Ensure your `DATABASE_URL` environment variable is set for `psycopg2` direct connections.

Run the Flask application:
```bash
flask run
# Or using gunicorn for production: gunicorn -w 4 'app:create_app()'
```
The backend API will typically run on `http://localhost:5000`. You can access the Swagger UI at `http://localhost:5000/docs`.

### 2. Frontend Setup

Navigate to the `frontend` directory:
```bash
cd frontend
```

Install frontend dependencies:
```bash
npm install
# or yarn install
```

Run the Vue development server:
```bash
npm run dev
# or yarn dev
```
The frontend application will typically run on `http://localhost:5173`. It is configured to proxy API requests to the backend at `http://localhost:5000`.

### 3. Running Tests

Navigate to the `backend` directory:
```bash
cd backend
```
Run pytest:
```bash
pytest
```

### Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── resources.py
│   │   ├── dao/ # Raw SQL data access layer
│   │   │   ├── __init__.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py (example model/schema)
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   ├── logging_config.yaml
│   ├── tests/ # New directory for pytest tests
│   │   ├── test_api.py # Example API tests
│   ├── requirements.txt
│   ├── pytest.ini
├── frontend/
│   ├── public/
│   │   ├── index.html
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── views/
│   │   ├── App.vue
│   │   ├── main.js
│   ├── package.json
│   ├── vue.config.js (for reference, Vite uses vite.config.js)
│   ├── vite.config.js
│   ├── README.md
├── .gitignore
├── README.md
```
""",
        )

        print(f"Project '{self.project_name}' generated successfully in {project_root}")
