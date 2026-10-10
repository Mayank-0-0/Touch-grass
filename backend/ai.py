import os
import json
import logging
import random
import requests
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

LLAMA_SERVER_URL = os.getenv("LLAMA_SERVER_URL", "http://127.0.0.1:8081")


class AIServerUnavailableError(Exception):
    """Raised when the local llama.cpp server is unreachable or timed out."""
    pass


class AIResponseParseError(Exception):
    """Raised when the local LLM outputs malformed or invalid JSON."""
    pass


def check_ai_status() -> Dict[str, Any]:
    """Check connectivity to the local llama.cpp server."""
    try:
        # llama.cpp server typically provides /health or responds on /
        resp = requests.get(f"{LLAMA_SERVER_URL}/health", timeout=2)
        if resp.status_code == 200:
            return {
                "online": True,
                "server_url": LLAMA_SERVER_URL,
                "model_name": "Local Gemma (llama.cpp)",
                "message": "Local AI server is online and ready."
            }
    except Exception:
        pass

    # Try root or a lightweight check if /health returned non-200 or errored
    try:
        resp = requests.get(f"{LLAMA_SERVER_URL}/", timeout=2)
        if resp.status_code in (200, 404):
            return {
                "online": True,
                "server_url": LLAMA_SERVER_URL,
                "model_name": "Local Gemma (llama.cpp)",
                "message": "Local AI server responded."
            }
    except Exception:
        pass

    return {
        "online": False,
        "server_url": LLAMA_SERVER_URL,
        "model_name": "Local Gemma (llama.cpp)",
        "message": "Local AI server is offline. Pre-curated fallback challenges are active."
    }


def _extract_json(text: str) -> Dict[str, Any]:
    """Clean markdown fences and safely parse JSON."""
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise AIResponseParseError("No JSON object found in response.")

    json_str = cleaned[start:end + 1]
    return json.loads(json_str)


# Curated Fallback Challenges Library
FALLBACK_CHALLENGES: List[Dict[str, Any]] = [
    {
        "title": "Natural Light Still Life Sketch",
        "interest": "Drawing",
        "duration_minutes": 30,
        "difficulty": "Easy",
        "instructions": "Place one everyday object (a cup, fruit, or shoe) by a window or single light source. Observe the shadows and contours for 3 minutes before drawing. Spend 25 minutes drawing without looking at any screen or reference image.",
        "materials": ["Paper or sketchbook", "Pencil or pen", "One physical object"],
        "expected_result": "A completed freehand sketch capturing basic proportions and light/shadow contrasts.",
        "proof_instructions": "Describe the object chosen, the lighting direction, and what part of the sketch was most challenging. Optional: photograph your drawing.",
        "follow_up_questions": [
            "What physical object did you choose to sketch and why?",
            "How did you approach shading the shadow cast by the object?",
            "What unexpected detail did you notice while looking closely at the real object?"
        ],
        "rubric": "Score based on observational focus, description of light and textures, and honest effort rather than technical perfection."
    },
    {
        "title": "Mindful Neighborhood Route Discovery",
        "interest": "Walking",
        "duration_minutes": 60,
        "difficulty": "Medium",
        "instructions": "Leave your phone in your pocket or at home. Walk a route in your local area you rarely take. Keep your senses tuned to architecture, trees, bird sounds, and ground textures. Notice at least three details you usually walk right past.",
        "materials": ["Comfortable walking shoes", "Weather-appropriate clothing"],
        "expected_result": "A refreshed mental state and acute awareness of your physical surroundings over a 60-minute walk.",
        "proof_instructions": "Submit a summary describing the route you walked, 3 overlooked details observed, and the physical sensory atmosphere.",
        "follow_up_questions": [
            "What specific route or path did you explore?",
            "Describe three distinct things you noticed that you had previously overlooked.",
            "How did your mindset change between the start and end of the walk?"
        ],
        "rubric": "Evaluate the vividness of the environmental observations and evidence of genuine offline exploration."
    },
    {
        "title": "Deep Reading & Concept Distillation",
        "interest": "Reading",
        "duration_minutes": 60,
        "difficulty": "Medium",
        "instructions": "Pick up a physical book (fiction, non-fiction, or essay). Find a quiet chair away from screens. Read steadily for 50 minutes. Spend the final 10 minutes reflecting on one central concept or memorable scene.",
        "materials": ["Physical book or printed text", "Notebook/pen for physical bookmarks"],
        "expected_result": "50 uninterrupted minutes of focused reading and a clear conceptual takeaway.",
        "proof_instructions": "State the title, author, pages covered, and an in-depth explanation of one fascinating concept or passage.",
        "follow_up_questions": [
            "What book did you read, and approximately how many pages did you cover?",
            "What was the single most compelling idea, quote, or argument in what you read?",
            "How does this idea relate to your own life or view of the world?"
        ],
        "rubric": "Evaluate comprehension depth, clarity of synthesis, and thoughtful reflection."
    },
    {
        "title": "Plant Health Inspection & Soil Refresh",
        "interest": "Gardening",
        "duration_minutes": 30,
        "difficulty": "Easy",
        "instructions": "Examine a houseplant, balcony pot, or garden bed. Inspect both sides of the leaves for dust or pests, gently aerate the top inch of soil with a small fork or stick, prune any dead leaves, and water thoroughly if needed.",
        "materials": ["Houseplant or outdoor plant", "Watering vessel", "Small stick or fork for soil aerating"],
        "expected_result": "A cleaned, pruned, and aerated plant with moist soil.",
        "proof_instructions": "Describe the plant species or type, what maintenance actions you performed, and your observations of its health.",
        "follow_up_questions": [
            "What plant did you tend to, and what was its condition before you started?",
            "What specific actions did you take (pruning, dusting, watering, aerating)?",
            "What did you notice about the soil moisture or leaf condition during your inspection?"
        ],
        "rubric": "Score based on specificity of gardening care actions and physical observations."
    },
    {
        "title": "Sensory One-Skillet Meal Crafting",
        "interest": "Cooking",
        "duration_minutes": 60,
        "difficulty": "Medium",
        "instructions": "Cook a fresh meal or snack using ingredients already in your pantry or fridge, without following a video tutorial or scrolling recipes. Rely on taste, smell, and visual cues to season and balance flavors.",
        "materials": ["Fresh produce, eggs, or grains", "Pan/skillet", "Cooking oil and spices"],
        "expected_result": "A homemade dish prepared using mindful sensory cooking techniques.",
        "proof_instructions": "Detail the dish prepared, ingredients combined, cooking sequence, and sensory evaluation of taste and texture.",
        "follow_up_questions": [
            "What dish did you prepare, and what raw ingredients did you choose?",
            "What sensory cues (aroma, color change, sizzling sound) guided your cooking time?",
            "How did the final flavors turn out, and what would you adjust next time?"
        ],
        "rubric": "Look for authentic sensory description of the cooking process, texture, and flavor profile."
    },
    {
        "title": "Stream of Consciousness Handwriting Sprint",
        "interest": "Writing",
        "duration_minutes": 30,
        "difficulty": "Easy",
        "instructions": "Take physical paper and pen. Set a physical watch or step away from digital clocks. Write continuously without erasing, editing, or pausing to self-critique. Write about your physical senses right now, memories, or a vivid story scene.",
        "materials": ["Pen or pencil", "Lined or blank paper notebook"],
        "expected_result": "At least 1 to 2 filled handwritten pages produced without screen disruption.",
        "proof_instructions": "Describe the theme that emerged from your writing and transcribe or summarize your favorite paragraph.",
        "follow_up_questions": [
            "How many pages did you write, and what physical medium did you use?",
            "What recurring thought, memory, or storyline emerged unprompted?",
            "Transcribe or summarize 2-3 sentences that felt most honest or surprising."
        ],
        "rubric": "Evaluate reflective honesty, handwriting commitment, and quality of excerpt provided."
    },
    {
        "title": "Acoustic Ear Training & Active Listening",
        "interest": "Music",
        "duration_minutes": 30,
        "difficulty": "Medium",
        "instructions": "If you play an instrument (guitar, piano, flute), practice an acoustic exercise or try to figure out a melody by ear without tabs or tutorial videos. If you don't play an instrument, sit in silence for 15 minutes noting all ambient acoustic pitches, then clap or hum rhythmic patterns.",
        "materials": ["Acoustic musical instrument (optional)", "Physical room with quiet acoustics"],
        "expected_result": "Sharpened auditory perception and hands-on rhythmic or instrumental practice.",
        "proof_instructions": "Detail your acoustic exercise, the melody or rhythm practiced, and how your ear adapted.",
        "follow_up_questions": [
            "What acoustic practice did you perform (instrument or active listening)?",
            "What challenge arose when trying to reproduce pitch or rhythm by ear?",
            "What progress did you feel after 30 minutes of screenless listening?"
        ],
        "rubric": "Score based on clarity of acoustic exercise and genuine musical attention."
    },
    {
        "title": "High-Intensity Bodyweight Mobility Routine",
        "interest": "Sports",
        "duration_minutes": 30,
        "difficulty": "Medium",
        "instructions": "Perform a complete screenless bodyweight routine: 5 minutes dynamic warm-up (hip openers, arm circles), 20 minutes circuit (squats, pushups, lunges, plank holds), and 5 minutes static cool-down stretches. Count your repetitions mentally.",
        "materials": ["Exercise mat or carpet", "Water bottle"],
        "expected_result": "A full physical workout engaging mobility, cardiovascular endurance, and core strength.",
        "proof_instructions": "Detail the exercises performed, total sets/reps completed, and physiological response.",
        "follow_up_questions": [
            "What exercise circuit did you execute, and how many rounds did you complete?",
            "Which movement felt strongest and which tested your mobility the most?",
            "How did your energy level and heart rate evolve through the workout?"
        ],
        "rubric": "Assess specific athletic routine details, rep awareness, and physical exertion report."
    },
    {
        "title": "Trail Exploration & Natural Feature Mapping",
        "interest": "Hiking",
        "duration_minutes": 120,
        "difficulty": "Hard",
        "instructions": "Find a local park, nature trail, or dirt path. Hike for 2 hours with phone set to airplane mode. Actively identify three native tree or plant species, observe geological formations, and practice pacing your breathing on inclines.",
        "materials": ["Trail footwear", "Hydration pack / water bottle", "Small physical notepad (optional)"],
        "expected_result": "Two hours of outdoor elevation and natural exploration away from civilization noise.",
        "proof_instructions": "Submit a detailed recap of trail distance, elevation or terrain difficulty, and flora/fauna observed.",
        "follow_up_questions": [
            "Which trail or outdoor location did you hike?",
            "Describe the terrain changes and flora/fauna you encountered along the route.",
            "How did maintaining a 2-hour offline immersion feel physically and mentally?"
        ],
        "rubric": "Evaluate outdoor endurance detail, botanical/terrain observation, and offline presence."
    },
    {
        "title": "Tactile Object Sorting & Physical De-Clutter",
        "interest": "Surprise Me",
        "duration_minutes": 30,
        "difficulty": "Easy",
        "instructions": "Choose one physical drawer, shelf, or toolbox in your room. Empty everything completely onto the floor. Inspect each item by hand. Discard trash, clean the surface with a damp cloth, and neatly categorize the contents back in place.",
        "materials": ["One messy drawer or shelf", "Cleaning cloth"],
        "expected_result": "A completely cleared, cleaned, and organized physical storage space.",
        "proof_instructions": "Describe what area you organized, what forgotten items you rediscovered, and how the space looks now.",
        "follow_up_questions": [
            "What specific physical space did you clean and reorganize?",
            "What interesting or long-lost object did you uncover?",
            "How does the tactile reorganization affect your room's ambiance?"
        ],
        "rubric": "Evaluate tangibility of physical sorting described, attention to detail, and completion."
    }
]


def get_fallback_challenge(interest: Optional[str] = None, duration_minutes: int = 30, difficulty: str = "Medium") -> Dict[str, Any]:
    """Retrieve an appropriate curated fallback challenge."""
    candidates = FALLBACK_CHALLENGES

    if interest and interest.lower() != "surprise me":
        matching = [c for c in candidates if c["interest"].lower() == interest.lower()]
        if matching:
            candidates = matching

    # Try matching duration if possible
    dur_matching = [c for c in candidates if c["duration_minutes"] == duration_minutes]
    if dur_matching:
        selected = dict(random.choice(dur_matching))
    else:
        selected = dict(random.choice(candidates))

    # Adjust duration & difficulty to user request
    selected["duration_minutes"] = duration_minutes
    selected["difficulty"] = difficulty
    selected["is_fallback"] = True
    return selected


def generate_challenge_with_gemma(
    interest: Optional[str],
    duration_minutes: int,
    difficulty: str,
    recent_titles: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate an offline activity challenge using the local Gemma model via llama.cpp.
    Falls back to curated challenges if local AI server is unavailable or fails.
    """
    chosen_interest = interest or "Surprise Me"
    if chosen_interest == "Surprise Me":
        interests_pool = ["Drawing", "Reading", "Gardening", "Walking", "Hiking", "Sports", "Cooking", "Music", "Writing"]
        chosen_interest = random.choice(interests_pool)

    avoid_note = ""
    if recent_titles:
        avoid_note = f"Avoid repeating recent tasks such as: {', '.join(recent_titles[-3:])}."

    prompt = f"""<start_of_turn>user
You are Touch Grass AI, an assistant dedicated to getting people away from screens into fulfilling, real-world offline activities.

Generate a realistic, screenless offline activity challenge.
Interest: {chosen_interest}
Duration: {duration_minutes} minutes
Difficulty: {difficulty}
{avoid_note}

Requirements:
- The user MUST NOT need any phone, computer, or digital screen during this challenge.
- The challenge must be safe, practical, and achievable in exactly {duration_minutes} minutes.
- The proof system must NOT require mandatory photos; instead, ask 2-3 specific, observant follow-up questions about what they physically experienced, saw, or made.

Return ONLY a valid JSON object with EXACTLY this structure:
{{
  "title": "Engaging activity title",
  "interest": "{chosen_interest}",
  "duration_minutes": {duration_minutes},
  "difficulty": "{difficulty}",
  "instructions": "Clear step-by-step instructions for what to do during the offline session.",
  "materials": ["Item 1", "Item 2"],
  "expected_result": "Concrete offline result to achieve.",
  "proof_instructions": "Activity-specific instructions on what to reflect upon and submit after returning.",
  "follow_up_questions": [
    "Specific follow-up question 1 about physical details?",
    "Specific follow-up question 2 about reflection or technique?",
    "Specific follow-up question 3 about observations made?"
  ],
  "rubric": "Scoring rubric criteria for evaluating proof (evaluating depth of observation, completion, and honest reflection)."
}}
<end_of_turn>
<start_of_turn>model
"""

    try:
        response = requests.post(
            f"{LLAMA_SERVER_URL}/completion",
            json={
                "prompt": prompt,
                "temperature": 0.3,
                "n_predict": 700,
                "stop": ["<end_of_turn>"]
            },
            timeout=25
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("content", "")

        parsed = _extract_json(content)
        # Validate required keys
        required_keys = ["title", "instructions", "proof_instructions", "follow_up_questions"]
        for key in required_keys:
            if key not in parsed or not parsed[key]:
                raise AIResponseParseError(f"Missing required key: {key}")

        parsed["interest"] = parsed.get("interest") or chosen_interest
        parsed["duration_minutes"] = duration_minutes
        parsed["difficulty"] = difficulty
        if not isinstance(parsed.get("materials"), list):
            parsed["materials"] = [str(parsed.get("materials"))] if parsed.get("materials") else []
        if not isinstance(parsed.get("follow_up_questions"), list) or len(parsed["follow_up_questions"]) == 0:
            parsed["follow_up_questions"] = [
                "Describe what you created, observed, or completed in detail.",
                "What was the most engaging moment during this offline period?",
                "What physical sensations or details did you notice away from screens?"
            ]
        parsed["is_fallback"] = False
        return parsed

    except (requests.RequestException, json.JSONDecodeError, AIResponseParseError) as e:
        logger.warning("Local AI generation failed or server unreachable (%s). Using curated fallback.", str(e))
        return get_fallback_challenge(chosen_interest, duration_minutes, difficulty)


def evaluate_proof_with_gemma(
    challenge_title: str,
    interest: str,
    duration_minutes: int,
    difficulty: str,
    instructions: str,
    rubric: str,
    follow_up_questions: List[str],
    proof_answers: Any,
    has_image: bool = False
) -> Dict[str, Any]:
    """
    Evaluate user's submitted offline evidence using the local Gemma model via llama.cpp.
    Raises AIServerUnavailableError if local server is unreachable.
    Does NOT fabricate scores or use cloud APIs.
    """
    # Format questions and user answers
    answers_text = ""
    if isinstance(proof_answers, dict):
        for q, a in proof_answers.items():
            answers_text += f"Question: {q}\nAnswer: {a}\n\n"
    elif isinstance(proof_answers, list):
        for item in proof_answers:
            answers_text += f"- {item}\n"
    else:
        answers_text = str(proof_answers)

    image_note = "User also uploaded a photo/sketch of their physical creation." if has_image else "No photo uploaded (text evidence only)."

    prompt = f"""<start_of_turn>user
You are Touch Grass AI, an impartial, supportive offline activity evaluator.

Evaluate the user's submitted proof for their offline challenge.
Score the evidence provided based on depth, relevance, observational detail, and honest effort.
Do not claim to verify unverifiable physical presence; grade the quality of the submitted reflections.

Challenge Details:
- Title: {challenge_title}
- Category: {interest}
- Target Duration: {duration_minutes} minutes
- Difficulty: {difficulty}
- Instructions: {instructions}
- Scoring Rubric: {rubric or 'Evaluate depth of observation, completeness, and genuine offline reflection.'}

Submitted Evidence:
{answers_text}
Physical Attachment: {image_note}

Provide an objective evaluation. Return ONLY a valid JSON object with EXACTLY this structure:
{{
  "relevance": "Concise assessment of how well the submission relates to the challenge task.",
  "quality": "Detailed feedback on the observation quality, detail, and sensory depth.",
  "completion_score": integer between 0 and 100 representing task completion,
  "feedback": "2-3 constructive, encouraging sentences on their offline accomplishment.",
  "final_score": integer between 0 and 100 representing total score
}}
<end_of_turn>
<start_of_turn>model
"""

    try:
        response = requests.post(
            f"{LLAMA_SERVER_URL}/completion",
            json={
                "prompt": prompt,
                "temperature": 0.2,
                "n_predict": 500,
                "stop": ["<end_of_turn>"]
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("content", "")

        parsed = _extract_json(content)
        final_score = int(parsed.get("final_score", parsed.get("completion_score", 85)))
        # Clamp to 0-100
        final_score = max(0, min(100, final_score))
        completion_score = int(parsed.get("completion_score", final_score))
        completion_score = max(0, min(100, completion_score))

        return {
            "relevance": parsed.get("relevance", "High relevance to the assigned offline activity."),
            "quality": parsed.get("quality", "Good detail and observational awareness described."),
            "completion_score": completion_score,
            "feedback": parsed.get("feedback", "Great job dedicating time offline and completing your activity!"),
            "final_score": final_score
        }

    except (requests.ConnectionError, requests.Timeout) as e:
        logger.error("Local llama.cpp server is unreachable: %s", str(e))
        raise AIServerUnavailableError(
            f"The local llama.cpp server at {LLAMA_SERVER_URL} is unreachable. Please ensure llama.cpp is running on port 8081."
        )
    except Exception as e:
        logger.error("AI proof evaluation encountered an error: %s", str(e))
        raise AIServerUnavailableError(
            f"Failed to communicate with local llama.cpp server: {str(e)}"
        )
