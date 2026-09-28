from app.config import DEMO_MODE, GEMINI_API_KEY, GEMINI_TIP_MODEL

SYSTEM_INSTRUCTION = """
You are FitBuddy's nutrition and recovery assistant.
Give concise general wellness advice. Do not provide calorie targets, restrictive diets,
supplement protocols, or medical treatment. Focus on balanced meals, hydration, sleep,
recovery, and sustainable habits. For users under 18, avoid weight-loss/body-composition
advice. Mention professional guidance when a health concern requires it.
"""


def generate_nutrition_tip_with_flash(goal: str, age: int) -> str:
    if DEMO_MODE:
        if age < 18:
            return "Tip: Keep meals balanced, drink water regularly, get enough sleep, and choose foods you enjoy. For health concerns, talk with a parent/guardian or qualified professional."
        return "Tip: Build balanced meals around a variety of foods, stay hydrated, and prioritize regular sleep and recovery alongside exercise."

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    from google import genai
    from google.genai import types
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
Give one concise nutrition or recovery tip for a person whose selected fitness goal is
"{goal}" and whose age is {age}. Keep it general, practical, and safe.
Do not provide calories, restrictive eating rules, or supplements.
"""
    response = client.models.generate_content(
        model=GEMINI_TIP_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.5,
            max_output_tokens=350,
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty nutrition tip.")
    return response.text.strip()
