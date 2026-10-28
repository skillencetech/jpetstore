from fastapi.templating import Jinja2Templates
from app.i18n import gettext_context, gettext

templates = Jinja2Templates(directory="app/templates")

# Register standard GNU gettext globals
templates.env.globals["_"] = gettext_context
templates.env.globals["gettext"] = gettext_context
templates.env.globals["t"] = gettext_context

# Register standard filters
templates.env.filters["_"] = gettext
templates.env.filters["gettext"] = gettext
templates.env.filters["t"] = gettext
