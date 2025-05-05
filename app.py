
from flask import Flask, request, jsonify
import os
import json
import logging
from datetime import datetime
import traceback
from dotenv import load_dotenv
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
    ]
)
logger = logging.getLogger(__name__)

def setup_environment_paths():
    """Sets up environment paths for saving files and configurations."""
    logger.debug("Setting up environment paths")
    try:
        os.environ["SEARCH_SAVE_FILE"] = os.path.join(os.getcwd(), "lib", "workspace", "alwrity_web_research",
                                                  f"web_research_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
        os.environ["IMG_SAVE_DIR"] = os.path.join(os.getcwd(), "lib", "workspace", "alwrity_content")
        os.environ["CONTENT_SAVE_DIR"] = os.path.join(os.getcwd(), "lib", "workspace", "alwrity_content")
        os.environ["PROMPTS_DIR"] = os.path.join(os.getcwd(), "lib", "workspace", "alwrity_prompts")
        os.environ["ALWRITY_CONFIG"] = os.path.join(os.getcwd(), "lib", "workspace", "alwrity_config", "main_config.json")
        logger.info("Environment paths configured successfully")
    except Exception as e:
        logger.error(f"Error setting up environment paths: {str(e)}", exc_info=True)
        raise



# Import your existing utilities (moved to separate modules)
# from lib.utils.api_key_manager.validation import check_api_key
# from lib.utils.core import setup_environment_paths

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()
setup_environment_paths()



# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "ALWrity API is running"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)