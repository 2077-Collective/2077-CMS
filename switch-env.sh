#!/bin/bash

# Function to validate environment name
validate_env() {
    if [[ ! "$1" =~ ^(local|production)$ ]]; then
        echo "Error: Invalid environment. Please specify 'local' or 'production'."
        exit 1
    fi
}

# Function to check file existence
check_file() {
    if [[ ! -f "$1" ]]; then
        echo "Error: $1 does not exist."
        exit 1
    fi
}

# Function to validate environment file contents
validate_env_file() {
    local file="$1"
    local required_vars=("DJANGO_SETTINGS_MODULE" "SECRET_KEY")
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" "$file"; then
            echo "Error: Missing required variable $var in $file"
            exit 1
        fi
    done

    # Optional: Warn if DEBUG is not set in production
    if [[ "$1" == "production" ]] && ! grep -q "^DEBUG=" "$file"; then
        echo "Warning: DEBUG is not set in .env.production. Defaulting to False."
        echo "DEBUG=False" >> "$file"
    fi
}

# Main script
if [[ -z "$1" ]]; then
    echo "Error: No environment specified. Please specify 'local' or 'production'."
    exit 1
fi

validate_env "$1"

source_file=".env.$1"
check_file "$source_file"

# Validate the environment file contents
validate_env_file "$source_file"

# Backup existing .env if it exists
if [[ -f .env ]]; then
    backup_file=".env.backup.$(date +%Y%m%d_%H%M%S)"
    cp .env "$backup_file"
    chmod 600 "$backup_file"  # Restrict to owner read/write only
    echo "Existing .env backed up to $backup_file"
fi

# Copy the specified environment file to .env
cp "$source_file" .env

# Verify the copy was successful
if [[ $? -eq 0 ]]; then
    echo "Successfully switched to $1 environment."
else
    echo "Error: Failed to switch environment."
    exit 1
fi