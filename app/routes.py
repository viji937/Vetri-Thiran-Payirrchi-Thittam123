from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pydantic import ValidationError

from app.config import ADMIN_KEY, DEMO_MODE
from app.database import (
    delete_user,
    get_all_plans,
    get_all_users,
    get_latest_plan,
    get_user,
    save_plan,
    save_user,
    update_plan,
)
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.gemini_generator import generate_workout_gemini
from app.schemas import FeedbackRequest, UserInput
from app.updated_plan import update_workout_plan
PROJECT_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=PROJECT_DIR / "templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request, "index.html",
        {"request": request, "demo_mode": DEMO_MODE},
    )


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):
    try:
        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
        workout_plan = generate_workout_gemini(
            data.username, data.age, data.weight, data.goal, data.intensity
        )
        nutrition_tip = generate_nutrition_tip_with_flash(data.goal, data.age)
        save_user(data.model_dump())
        save_plan(data.user_id, workout_plan, nutrition_tip)

        return templates.TemplateResponse(
            request, "result.html",
            {
                "request": request,
                "user": data,
                "workout_plan": workout_plan,
                "nutrition_tip": nutrition_tip,
                "updated_plan": None,
                "message": "Your plan was generated successfully.",
            },
        )
    except ValidationError as exc:
        return templates.TemplateResponse(
            request, "index.html",
            {
                "request": request,
                "demo_mode": DEMO_MODE,
                "error": "Please check the form values and try again.",
                "details": str(exc),
            },
            status_code=422,
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request, "index.html",
            {
                "request": request,
                "demo_mode": DEMO_MODE,
                "error": "The plan could not be generated.",
                "details": str(exc),
            },
            status_code=500,
        )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
):
    try:
        form = FeedbackRequest(user_id=user_id, feedback=feedback)
        user = get_user(form.user_id)
        plan = get_latest_plan(form.user_id)

        if not user or not plan:
            return templates.TemplateResponse(
                "result.html",
                {
                    "request": request,
                    "error": "No saved plan was found for that User ID.",
                },
                status_code=404,
            )

        revised = update_workout_plan(
            plan.original_plan,
            form.feedback,
            user.goal,
            user.age,
            user.intensity,
        )
        update_plan(form.user_id, revised, form.feedback)

        return templates.TemplateResponse(
            request, "result.html",
            {
                "request": request,
                "user": user,
                "workout_plan": plan.original_plan,
                "updated_plan": revised,
                "nutrition_tip": plan.nutrition_tip,
                "message": "Your plan was updated using the feedback.",
            },
        )
    except ValidationError:
        return templates.TemplateResponse(
            request, "result.html",
            {"request": request, "error": "Please enter valid feedback."},
            status_code=422,
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request, "result.html",
            {"request": request, "error": f"Could not update the plan: {exc}"},
            status_code=500,
        )


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, key: str = Query(default="")):
    if key != ADMIN_KEY:
        return templates.TemplateResponse(
            request, "admin_login.html",
            {"request": request, "error": "Invalid admin key."},
            status_code=403,
        )

    users = get_all_users()
    plans = {p.user_id: p for p in get_all_plans()}
    return templates.TemplateResponse(
        request, "all_users.html",
        {"request": request, "users": users, "plans": plans, "admin_key": key},
    )


@router.post("/admin/delete-user", response_class=HTMLResponse)
def admin_delete_user(
    request: Request,
    user_id: str = Form(...),
    key: str = Form(...),
):
    if key != ADMIN_KEY:
        return templates.TemplateResponse(
            request, "admin_login.html",
            {"request": request, "error": "Invalid admin key."},
            status_code=403,
        )
    delete_user(user_id)
    return RedirectResponse(url=f"/view-all-users?key={key}", status_code=303)


@router.get("/health")
def health():
    return {"status": "ok", "service": "fitbuddy", "demo_mode": DEMO_MODE}
