from app.config import DEMO_MODE, GEMINI_API_KEY, GEMINI_PLAN_MODEL
from app.gemini_generator import SYSTEM_INSTRUCTION


def update_workout_plan(original_plan: str, feedback: str, goal: str, age: int, intensity: str) -> str:
    if DEMO_MODE:
        return f"""Updated FitBuddy Plan

Your feedback was:
{feedback}

The plan has been adjusted while keeping the original goal ({goal}) and intensity ({intensity}).

Suggested changes:
- Keep the same overall weekly structure.
- Increase or decrease exercise volume gradually rather than making a sudden jump.
- Add more mobility or comfortable cardio if requested.
- Preserve at least one recovery-focused day.
- Stop if pain, dizziness, fainting, or unusual symptoms occur.

For users under 18, focus on enjoyable movement and healthy routines rather than weight loss or body composition.
"""

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    from google import genai
    from google.genai import types
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
Update this existing 7-day fitness plan using the user's feedback.

Age: {age}
Goal: {goal}
Intensity: {intensity}

ORIGINAL PLAN:
{original_plan}

USER FEEDBACK:
{feedback}

Return a complete revised 7-day plan, not just a list of edits.
Keep the plan safe and sustainable. Do not prescribe calories, restrictive dieting,
supplements, dangerous challenges, or extreme exercise. Preserve recovery days.
If the user is under 18, keep the plan focused on general wellness and enjoyable movement.
"""
    response = client.models.generate_content(
        model=GEMINI_PLAN_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.6,
            max_output_tokens=5000,
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty updated plan.")
    return response.text.strip()
