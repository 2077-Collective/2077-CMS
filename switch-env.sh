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

# Main script
if [[ -z "$1" ]]; then
    echo "Error: No environment specified. Please specify 'local' or 'prod'."
    exit 1
fi

validate_env "$1"

source_file=".env.$1"
check_file "$source_file"

# Backup existing .env if it exists
if [[ -f .env ]]; then
    backup_file=".env.backup.$(date +%Y%m%d_%H%M%S)"
    cp .env "$backup_file"
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