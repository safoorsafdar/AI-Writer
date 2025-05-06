
from flask import Flask, request, jsonify
import os
import json
import logging
from datetime import datetime
import traceback
from dotenv import load_dotenv
from functools import wraps

from lib.ai_writers.ai_facebook_writer.modules.post_generator import FacebookPostGenerator
from lib.ai_writers.linkedin_writer.modules.post_generator.linkedin_post_generator import LinkedInPostGenerator

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


@app.route('/api/generate-linkedin-post', methods=['POST'])
def generate_linkedin_post():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract parameters
        topic = data.get("topic")
        industry = data.get("industry")
        tone = data.get("tone", "Professional")
        include_hashtags = data.get("include_hashtags", True)
        include_visual = data.get("include_visual", True)
        include_poll = data.get("include_poll", False)
        include_timing = data.get("include_timing", True)
        search_engine = data.get("search_engine", "metaphor").lower()

        if not topic or not industry:
            return jsonify({"error": "Both 'topic' and 'industry' are required"}), 400

        generator = LinkedInPostGenerator()

        # Research
        research_results = generator.research_topic(topic, industry, search_engine)

        # Outline and content generation
        outline = generator.generate_outline(research_results)
        post_content = generator.generate_post_content(outline, tone, include_hashtags)

        # Hashtags
        hashtags = generator.optimize_hashtags(post_content) if include_hashtags else []

        # Visual Content
        visual_content = None
        image_path = None
        if include_visual:
            visual_content = generator.generate_visual_content(post_content, topic)
            if visual_content and "main_image" in visual_content:
                image_path = generator.generate_image(visual_content["main_image"]["prompt"])

        # Image prompts from post
        image_prompts = generator._extract_image_prompts_from_post(post_content)

        # Build response
        response = {
            "success": True,
            "post": {
                "topic": topic,
                "industry": industry,
                "tone": tone,
                "content": post_content,
                "hashtags": hashtags,
                "visual_content": visual_content,
                "image_path": image_path,
                "image_prompts": image_prompts,
                "posting_time_suggestion": "Tuesday-Thursday, 9:00 AM - 11:00 AM" if include_timing else None,
                "engagement_prediction": "This post is predicted to perform well based on current LinkedIn trends." if include_timing else None
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error generating LinkedIn post: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500



@app.route('/api/generate-facebook-post', methods=['POST'])
def generate_facebook_post():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract required parameters
        business_type = data.get("business_type")
        target_audience = data.get("target_audience")
        
        if not business_type or not target_audience:
            return jsonify({"error": "Both 'business_type' and 'target_audience' are required"}), 400
        
        # Create generator instance
        generator = FacebookPostGenerator()
        
        # Generate post
        post_result = generator.generate_post(data)
        
        # Build response
        response = {
            "success": True,
            "post": {
                "business_type": business_type,
                "target_audience": target_audience,
                "post_goal": data.get("post_goal", "Increase engagement"),
                "post_tone": data.get("post_tone", "Upbeat"),
                "content": post_result["content"],
                "media_type": data.get("media_type", "None"),
                "media_settings": data.get("media_settings", {}),
                "engagement_predictions": post_result["engagement_predictions"],
                "optimization_suggestions": post_result["optimization_suggestions"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error generating Facebook post: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-tweets', methods=['POST'])
def generate_tweets():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract parameters
        hook = data.get("hook")
        target_audience = data.get("target_audience", "General")
        tone = data.get("tone", "Professional")
        call_to_action = data.get("call_to_action", "")
        keywords = data.get("keywords", "")
        length = data.get("length", "medium")
        num_variations = data.get("num_variations", 3)
        
        if not hook:
            return jsonify({"error": "Tweet hook/topic is required"}), 400
        
        # Validate number of variations
        if not isinstance(num_variations, int) or num_variations < 1 or num_variations > 5:
            return jsonify({"error": "Number of variations must be between 1 and 5"}), 400
        
        # Create generator instance
        generator = SmartTweetGenerator()
        
        # Generate tweet variations
        tweets = generator.generate_tweet_variations(
            hook, target_audience, tone,
            call_to_action, keywords, length,
            num_variations
        )
        
        # Add performance metrics and suggestions for each tweet
        enriched_tweets = []
        for tweet in tweets:
            performance = generator.predict_tweet_performance(tweet["text"], target_audience, tone)
            suggestions = generator.suggest_improvements(tweet["text"], performance)
            
            enriched_tweets.append({
                "id": tweet["id"],
                "text": tweet["text"],
                "metrics": tweet["metrics"],
                "performance": performance,
                "suggestions": suggestions
            })
        
        # Build response
        response = {
            "success": True,
            "tweets": enriched_tweets,
            "request": {
                "hook": hook,
                "target_audience": target_audience,
                "tone": tone,
                "call_to_action": call_to_action,
                "keywords": keywords,
                "length": length,
                "num_variations": num_variations
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error generating tweets: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)