"""
Setup script for Crop Recommendation System
"""
import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and log the result."""
    logger.info(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ {description} failed: {e.stderr}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = ['logs', 'staticfiles', 'media']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def setup_environment():
    """Set up environment file."""
    env_file = '.env'
    if not os.path.exists(env_file):
        logger.info("Creating .env file from template...")
        with open('env_example.txt', 'r') as f:
            content = f.read()
        with open(env_file, 'w') as f:
            f.write(content)
        logger.info("✓ .env file created. Please edit it with your configuration.")
    else:
        logger.info("✓ .env file already exists")

def main():
    """Main setup function."""
    logger.info("🚀 Setting up Crop Recommendation System...")
    
    # Create directories
    create_directories()
    
    # Setup environment
    setup_environment()
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        logger.error("Failed to install dependencies. Please check your Python environment.")
        return False
    
    # Make migrations
    if not run_command("python manage.py makemigrations", "Creating database migrations"):
        logger.error("Failed to create migrations.")
        return False
    
    # Run migrations
    if not run_command("python manage.py migrate", "Running database migrations"):
        logger.error("Failed to run migrations. Please check your database configuration.")
        return False
    
    # Train ML models
    if not run_command("python ml/train.py", "Training ML models"):
        logger.warning("Failed to train ML models. The system will use fallback predictions.")
    
    logger.info("🎉 Setup completed successfully!")
    logger.info("Next steps:")
    logger.info("1. Edit .env file with your database and API configuration")
    logger.info("2. Create a superuser: python manage.py createsuperuser")
    logger.info("3. Start the server: python manage.py runserver")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
