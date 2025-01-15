![](./2077.webp)

# 2077 Collective

Content management system written in Python(Django) and Sveltekit

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

    # Beehiiv Integration
    BEEHIIV_ENABLED=True
    BEEHIIV_API_KEY=your_beehiiv_api_key  # Get this from Beehiiv dashboard
    BEEHIIV_PUBLICATION_ID=your_publication_id  # Get this from Beehiiv dashboard
    BEEHIIV_SYNC_BATCH_SIZE=50
   ```

5. Environment Switching: Use this script (switch-env.sh) to easily switch between environments:

   Before using the script, create your environment files:
   1. Copy `.env.example` to `.env.local` and `.env.production`
   2. Update each file with appropriate values
   3. Use the script to switch between environments

   ```sh
   #!/bin/bash

   validate_env() {
       if [[ ! "$1" =~ ^(local|production)$ ]]; then
           echo "Error: Invalid environment. Please specify 'local' or 'production'."
           exit 1
       fi
   }

   check_file() {
       if [[ ! -f "$1" ]]; then
           echo "Error: $1 does not exist."
           exit 1
       fi
   }

   validate_env_file() {
       local file="$1"
       local required_vars=("DJANGO_SETTINGS_MODULE" "SECRET_KEY")

       for var in "${required_vars[@]}"; do
           if ! grep -q "^${var}=" "$file"; then
               echo "Error: Missing required variable $var in $file"
               exit 1
           fi
       done

       if [[ "$1" == "production" ]] && ! grep -q "^DEBUG=" "$file"; then
           echo "Warning: DEBUG is not set in .env.production. Defaulting to False."
           echo "DEBUG=False" >> "$file"
       fi
   }

   if [[ -z "$1" ]]; then
       echo "Error: No environment specified. Please specify 'local' or 'production'."
       exit 1
   fi

   validate_env "$1"

   source_file=".env.$1"
   check_file "$source_file"

   validate_env_file "$source_file"

   if [[ -f .env ]]; then
       backup_file=".env.backup.$(date +%Y%m%d_%H%M%S)"
       cp .env "$backup_file"
       chmod 600 "$backup_file"  # Restrict to owner read/write only
       echo "Existing .env backed up to $backup_file"
   fi

   cp "$source_file" .env

   if [[ $? -eq 0 ]]; then
       echo "Successfully switched to $1 environment."
   else
       echo "Error: Failed to switch environment."
       exit 1
   fi
      ```

   ### Usage
   Make script executable:

   ```sh
      chmod +x switch-env.sh
   ```

   1. Set restrictive permissions for environment files:
   ```sh
      chmod 600 .env.local .env.production .env
   ```
   This ensures that only the file owner can read or modify these files, protecting sensitive information.

   2. Switch to the desired environment:
   ./switch-env.sh local  # Switch to local environment
   ./switch-env.sh production   # Switch to production environment
   ```

   ### What the Script Does:
      - Validates the Environment Name: Ensures only local or production environments are specified.

      - Checks for Required Variables: Validates that the environment file (e.g., .env.production) contains all required variables (DJANGO_SETTINGS_MODULE, SECRET_KEY, and DEBUG).

      - Backs Up the Existing .env File: If a .env file already exists, it is backed up with a timestamp.

      - Switches the Environment: Copies the specified environment file to .env.

   ### Example:
      ```sh
         ./switch-env.sh production
      ```
   ### Output:
      - **If successful**:
      ```sh
         Existing .env backed up to .env.backup.20231025_123456
         Successfully switched to production environment.
      ```
      - If a required variable is missing:
      ```sh
         Error: Missing required variable DEBUG in .env.production
      ```

   ### Required Variables:
   Ensure your environment files (e.g., .env.local, .env.production) include the following variables:
   ```sh
      DJANGO_SETTINGS_MODULE=core.config.local  # or core.config.production for production
      SECRET_KEY=your-secret-key-here
      DEBUG=True  # or False for production
   ```
   For production, it is recommended to set DEBUG=False for security reasons.


6. Run the application:

- Start Server:

  ```bash
  python3 manage.py makemigrations # To compile the migrations
  python3 manage.py migrate  # To migrate the changes in Database
  python3 manage.py runserver # To run the API server
  redis-server # to start redis-server
  celery -A core worker -Q default,beehiiv -l info # to run celery with beehiiv queue
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
   |  POST  | newsletter/subscribe/ | Subscribe to newsletter |

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

Work in Progress...stay tuned
