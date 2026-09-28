from app.config import DEMO_MODE, GEMINI_API_KEY, GEMINI_PLAN_MODEL

SYSTEM_INSTRUCTION = """
You are FitBuddy, an AI fitness-planning assistant.

Safety rules:
- Provide general wellness and fitness education, not diagnosis or treatment.
- Never recommend dangerous stunts, extreme exercise, starvation, purging, dehydration,
  unsafe supplements, or rapid body-change tactics.
- Do not give calorie targets or restrictive meal plans.
- Prefer sustainable movement, rest, hydration, balanced eating, and gradual progression.
- For users under 18, avoid weight-loss/body-composition coaching and focus on enjoyable
  movement, general strength, mobility, sleep, hydration, and healthy routines.
- Include a brief reminder to stop if there is pain, dizziness, fainting, or unusual symptoms
  and seek help from a trusted adult/qualified professional when appropriate.
- Make plans adaptable and beginner-friendly.
"""


def _client():
    from google import genai
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=GEMINI_API_KEY)


def demo_workout(username: str, goal: str, intensity: str, age: int) -> str:
    focus = "general wellness" if age < 18 else goal
    return f"""FitBuddy 7-Day Plan for {username}

Goal focus: {focus}
Intensity: {intensity}

Day 1 – Full-body movement
- Warm-up: 5–8 minutes of easy walking and mobility
- Main: bodyweight squats, wall/incline push-ups, glute bridges, bird-dogs
- 2–3 comfortable rounds; rest as needed
- Cool-down: gentle stretching

Day 2 – Cardio + mobility
- 20–30 minutes of comfortable walking, cycling, or another enjoyable activity
- 5–10 minutes of gentle mobility

Day 3 – Strength basics
- Warm-up: 5–8 minutes
- Main: sit-to-stand/squats, rows with a safe resistance option, calf raises, dead-bug
- 2–3 comfortable rounds
- Cool-down: easy stretching

Day 4 – Recovery
- Easy walk or light mobility for 15–25 minutes
- Prioritize sleep, hydration, and recovery

Day 5 – Full-body movement
- Warm-up: 5–8 minutes
- Repeat a few familiar movements from Days 1 and 3 at a comfortable effort
- Cool-down: gentle stretching

Day 6 – Fun activity
- Choose a safe activity you enjoy for 20–40 minutes
- Keep the effort comfortable enough to maintain good form

Day 7 – Rest and reset
- Optional easy walk and gentle mobility
- Reflect on what felt comfortable and what you would like to adjust next week

Safety note: Stop if you feel pain, dizziness, fainting, or unusual symptoms.
This is general wellness guidance, not medical advice.
"""


def generate_workout_gemini(username: str, age: int, weight: float, goal: str, intensity: str) -> str:
    if DEMO_MODE:
        return demo_workout(username, goal, intensity, age)

    prompt = f"""
Create a personalized but safety-conscious 7-day fitness plan.

User:
- Name: {username}
- Age: {age}
- Weight: {weight} kg
- Goal: {goal}
- Preferred intensity: {intensity}

Requirements:
1. Use exactly 7 labeled days.
2. Each day should include a warm-up, main activity, and cool-down/recovery guidance.
3. Give simple exercise names, sets/repetitions or time, and rest guidance.
4. Include at least one recovery/rest-focused day.
5. Do not prescribe calories, restrictive dieting, supplements, or unsafe intensity.
6. If age is under 18, do not coach weight loss or body composition; use a general wellness focus.
7. Keep the answer readable in plain text.
"""
    from google.genai import types
    response = _client().models.generate_content(
        model=GEMINI_PLAN_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.6,
            max_output_tokens=5000,
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty workout plan.")
    return response.text.strip()
