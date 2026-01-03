#!/bin/bash
# Database setup script for TravelBuddy backend
# This script creates the database, user, and runs the schema

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
DB_NAME="travelbuddy"
DB_USER="travelbuddy"
DB_PASSWORD=""
SCHEMA_FILE="database/schema.sql"
SKIP_USER_CREATE=false
SKIP_SCHEMA=false

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --db-name)
            DB_NAME="$2"
            shift 2
            ;;
        --db-user)
            DB_USER="$2"
            shift 2
            ;;
        --db-password)
            DB_PASSWORD="$2"
            shift 2
            ;;
        --schema-file)
            SCHEMA_FILE="$2"
            shift 2
            ;;
        --skip-user-create)
            SKIP_USER_CREATE=true
            shift
            ;;
        --skip-schema)
            SKIP_SCHEMA=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --db-name NAME          Database name (default: travelbuddy)"
            echo "  --db-user USER          Database user (default: travelbuddy)"
            echo "  --db-password PASSWORD  Database password (will prompt if not provided)"
            echo "  --schema-file PATH      Path to schema file (default: database/schema.sql)"
            echo "  --skip-user-create      Skip user creation (user already exists)"
            echo "  --skip-schema           Skip schema execution"
            echo "  -h, --help             Show this help message"
            echo ""
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BACKEND_DIR"

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then
    print_warn "Running as root. Will use postgres user for database operations."
    POSTGRES_CMD=""
else
    # Check if we can run sudo
    if ! sudo -n true 2>/dev/null; then
        print_info "This script requires sudo privileges for database setup."
        print_info "You will be prompted for your password."
    fi
    POSTGRES_CMD="sudo -u postgres"
fi

# Prompt for password if not provided
if [ -z "$DB_PASSWORD" ]; then
    read -sp "Enter password for database user '$DB_USER': " DB_PASSWORD
    echo ""
    if [ -z "$DB_PASSWORD" ]; then
        print_error "Password cannot be empty"
        exit 1
    fi
fi

print_info "Setting up database: $DB_NAME"
print_info "Database user: $DB_USER"
print_info "Schema file: $SCHEMA_FILE"

# Check if PostgreSQL is running
print_info "Checking if PostgreSQL is running..."
if ! $POSTGRES_CMD psql -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw postgres; then
    print_error "PostgreSQL is not running or not accessible"
    print_info "Try: sudo systemctl start postgresql"
    exit 1
fi
print_info "PostgreSQL is running"

# Create database user
if [ "$SKIP_USER_CREATE" = false ]; then
    print_info "Creating database user '$DB_USER'..."
    
    # Check if user already exists
    USER_EXISTS=$($POSTGRES_CMD psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" 2>/dev/null || echo "")
    
    if [ "$USER_EXISTS" = "1" ]; then
        print_warn "User '$DB_USER' already exists. Updating password..."
        $POSTGRES_CMD psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || {
            print_error "Failed to update password. User may not have sufficient privileges."
            exit 1
        }
    else
        $POSTGRES_CMD psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || {
            print_error "Failed to create user"
            exit 1
        }
        print_info "User created successfully"
    fi
else
    print_info "Skipping user creation (--skip-user-create flag set)"
fi

# Create database
print_info "Creating database '$DB_NAME'..."
DB_EXISTS=$($POSTGRES_CMD psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>/dev/null || echo "")

if [ "$DB_EXISTS" = "1" ]; then
    print_warn "Database '$DB_NAME' already exists"
    read -p "Do you want to drop and recreate it? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_warn "Dropping existing database..."
        $POSTGRES_CMD psql -c "DROP DATABASE IF EXISTS $DB_NAME;"
        $POSTGRES_CMD psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
        print_info "Database recreated"
    else
        print_info "Using existing database"
    fi
else
    $POSTGRES_CMD psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" 2>/dev/null || {
        print_error "Failed to create database"
        exit 1
    }
    print_info "Database created successfully"
fi

# Grant privileges
print_info "Granting privileges..."
$POSTGRES_CMD psql -d "$DB_NAME" << EOF
-- Grant database privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO $DB_USER;

-- Make user owner of schema (most permissive)
ALTER SCHEMA public OWNER TO $DB_USER;
EOF

print_info "Privileges granted"

# Run schema
if [ "$SKIP_SCHEMA" = false ]; then
    if [ ! -f "$SCHEMA_FILE" ]; then
        print_error "Schema file not found: $SCHEMA_FILE"
        exit 1
    fi
    
    print_info "Running schema file: $SCHEMA_FILE"
    $POSTGRES_CMD psql -d "$DB_NAME" -f "$SCHEMA_FILE" || {
        print_error "Failed to run schema"
        exit 1
    }
    print_info "Schema executed successfully"
else
    print_info "Skipping schema execution (--skip-schema flag set)"
fi

# Verify setup
print_info "Verifying setup..."
TABLES=$($POSTGRES_CMD psql -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null || echo "0")

if [ "$TABLES" -gt "0" ]; then
    print_info "Found $TABLES table(s) in database"
    $POSTGRES_CMD psql -d "$DB_NAME" -c "\dt" 2>/dev/null || true
else
    print_warn "No tables found in database"
fi

# Test connection
print_info "Testing connection..."
export PGPASSWORD="$DB_PASSWORD"
if psql -U "$DB_USER" -d "$DB_NAME" -h localhost -c "SELECT 1;" > /dev/null 2>&1; then
    print_info "Connection test successful!"
else
    print_warn "Connection test failed. You may need to configure pg_hba.conf for password authentication."
    print_info "Edit: sudo nano /etc/postgresql/*/main/pg_hba.conf"
    print_info "Change 'peer' to 'md5' for local connections"
    print_info "Then restart: sudo systemctl restart postgresql"
fi
unset PGPASSWORD

# Display connection string
echo ""
print_info "Setup complete!"
echo ""
print_info "Database connection string:"
echo "  postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
print_info "Add this to your .env file:"
echo "  DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""

