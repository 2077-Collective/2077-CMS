![](./2077.webp)

# 2077 Collective

Content management system written in Python(Django) and React.js

## Project Architecture

![architecture](./cms%202077%20architecture.webp)

## Prerequisites

Before running the application, ensure you have the following:

- Git (for version control)
- Node.js runtime environment
- Python3 and pip3

## Running the App

1. Clone the repository

   ```bash
   git clone https://github.com/2077-Collective/2077cms.git
   cd 2077cms
   ```

2. Create virtual environment

- For Linux/MacOS,

  ```bash
  cd server # enter the server directory
  python3 -m venv .venv
  source .venv/bin/activate
  ```

- For Windows,

  ```bash
  cd server # enter the server directory
  pip3 install virtualenv
  virtualenv myenv
  myenv\Scripts\activate
  ```

3. Install dependencies for the project:

   ```bash
    pip3 install -r requirements.txt
   ```

4. Setup Environment Variables:

   Create a .env file in the root directory using the .env.example template and add all required variables:

   ```env
    DJANGO_SETTINGS_MODULE='core.config.local' #for Dev environment

    # Sqlite3 database config
    SECRET_KEY='paste db.sqlite3 key here'

    # Production-Only Env Database config
    # PostgreSql Credentials
    DB_NAME=<enter database name>
    DB_USER=<enter username>
    DB_PASS=<enter password>
    DB_HOST=localhost
    DB_PORT=5432

    SITE_URL='http://localhost:8000'

    # Django smtp
    EMAIL_HOST = 'smtp.gmail.com' # Example using Gmail
    EMAIL_HOST_USER = 'enter your email'
    EMAIL_HOST_PASSWORD = 'enter password' #for Gmail, generate app password
   ```

5. Run the application in development mode:

- Start Server:

  ```bash
  python3 manage.py makemigrations # To compile the migrations
  python3 manage.py migrate  # To migrate the changes in Database
  python3 manage.py runserver # To run the API server
  redis-server # to start redis-server
  celery -A core worker -l info # to run celery
  celery -A core beat -l info # to run celery beat
  ```

- Start Research Client:

  ```bash
  cd research # enter the research directory
  npm install pnpm # do this if you dont have pnpm installed
  pnpm install
  pnpm start # To run the the research server
  ```

6. API Testing: `http://127.0.0.1:8000/api/<ROUTE>`

   | Method |       Route        |     Description     |
   | :----: | :----------------: | :-----------------: |
   |  GET   |     articles/      |  List all articles  |
   |  POST  |     articles/      |   Add an article    |
   |  GET   | articles/<uuid:pk> | Retrieve an article |
   | PATCH  | articles/<uuid:pk> |  Update an article  |
   | DELETE | articles/<uuid:pk> |  Delete an article  |

7. Client Testing: `http://localhost:4321`

   | Method |   Route   |     Description     |
   | :----: | :-------: | :-----------------: |
   |  GET   |     /     |  List all articles  |
   |  GET   | <uuid:pk> | Retrieve an article |

8. Model Testing: run `python manage.py test`

9. Contributing

If you want to contribute to this project, please read the [contribution guide](./CONTRIBUTING.md).

### Code Style

- Follow PEP 8 for Python code

### Pull Request Process

- Create a new branch for your feature or fix
- Submit a pull request with a clear description

## License and Credits

- Licensed under the MIT License
- Uses third-party libraries: Django, React, etc.

## Troubleshooting

### Common Errors

- "Module not found" error: Check your dependencies and installation
- "React-Scripts Dependencies error" : Install using `--legacy-peer-deps`

Working in Progress...stay tuned

Does it work?
