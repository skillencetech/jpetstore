from fastapi.templating import Jinja2Templates
from app.i18n import t_context, translate_text

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["t"] = t_context
templates.env.filters["t"] = translate_text
