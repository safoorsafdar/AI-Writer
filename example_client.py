import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
API_BASE_URL = "http://localhost:5000"
API_KEY = os.getenv("ALWRITY_API_KEY")

# Headers for authenticated requests
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def check_health():
    """Check if the API is running"""
    response = requests.get(f"{API_BASE_URL}/health")
    print("Health Check:", response.json())
    return response.json()
    


if __name__ == "__main__":
    # Example usage
    print("===== ALwrity API Client Example =====")
    
    # Check if API is running
    check_health()
    
    # Note: To get specific content, you would need an actual filename
    # Uncomment this once you have generated content and know a filename
    # get_content("blog_post_2025-05-05_12-34-56.json")