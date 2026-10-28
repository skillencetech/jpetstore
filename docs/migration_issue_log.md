# JPetStore 6 Modernization: Migration & Resolution Issue Log

**Project:** JPetStore 6 AI-Native Modernization  
**Repository:** `C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore`  
**Target Environment:** Python 3.15 (Windows AMD64), FastAPI, SQLAlchemy 2.0, Jinja2  
**Last Updated:** 2026-10-28  

---

## Executive Summary of Technical Issues & Resolutions

| # | Issue Summary | Category | Impact | Status | Fix Commit |
| :- | :--- | :---: | :---: | :---: | :---: |
| **01** | Python runtime missing / Windows app execution aliases active | Environment | Blocking | **Resolved** | System setup |
| **02** | C-Extension wheel build failures on Python 3.15 (`pyyaml`, `argon2-cffi`) | Dependencies | Blocking | **Resolved** | [`64e4146`](#issue-02-c-extension-wheel-build-failures-on-python-315) |
| **03** | Missing SQLAlchemy async coroutine dependency (`greenlet`) | Dependencies | Blocking | **Resolved** | [`12b8d6a`](#issue-03-missing-sqlalchemy-asyncio-dependency-greenlet) |
| **04** | Breaking signature change in Starlette `TemplateResponse` | Framework | Runtime 500 | **Resolved** | [`ef06ce7`](#issue-04-starlette-036-breaking-signature-change-in-templateresponse) |
| **05** | Cart page CSS float collapse & footer intrusion | UI / Layout | Visual regression | **Resolved** | [`80f3847`](#issue-05-cart-page-css-float-collapse--footer-misalignment) |
| **06** | Async SQLAlchemy `MissingGreenlet` during template rendering | Persistence / ORM | Runtime 500 | **Resolved** | [`ca9596b`](#issue-06-async-sqlalchemy-missinggreenlet-during-order-view) |

---

## Detailed Issue Breakdown

### Issue 01: Python Runtime Missing / Windows App Execution Aliases
* **Symptom:** Terminal command output: `Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Apps > Advanced app settings > App execution aliases.`
* **Root Cause:** Windows fresh developer environment had placeholder Microsoft Store alias stubs active with no Python binary registered in system `PATH`.
* **Resolution:** Installed Python 3.15 via `winget install Python.Python.3.12` and initialized dedicated virtual environment (`venv`).

---

### Issue 02: C-Extension Wheel Build Failures on Python 3.15
* **Symptom:** `pip install -r requirements.txt` failed with `error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools"` while compiling `pyyaml` and `argon2-cffi`.
* **Root Cause:** 
  1. `uvicorn[standard]` pulled optional C-accelerators (`pyyaml`, `httptools`, `watchfiles`) that lacked pre-built binary wheels for Python 3.15 Windows AMD64, triggering source compilation with Cython.
  2. `passlib[argon2]` required CFFI C headers.
* **Resolution (Commit `64e4146`):**
  1. Replaced `uvicorn[standard]` with pure-Python `uvicorn>=0.28.0`.
  2. Migrated password hashing in [app/services/account_service.py](file:///C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore/app/services/account_service.py) to Python's standard library `hashlib.scrypt` (OWASP-recommended memory-hard hashing, zero C-compiler dependencies, with legacy plaintext auto-upgrading).

---

### Issue 03: Missing SQLAlchemy Asyncio Dependency (`greenlet`)
* **Symptom:** `ImportError: The SQLAlchemy asyncio module requires that the Python 'greenlet' library is installed. In order to ensure this dependency is available, use the 'sqlalchemy[asyncio]' install target.`
* **Root Cause:** SQLAlchemy 2.0 async engine (`create_async_engine`) uses greenlet coroutine context switching underneath, which is an optional extra if not explicitly specified.
* **Resolution (Commit `12b8d6a`):**
  - Updated [requirements.txt](file:///C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore/requirements.txt) to explicitly include `sqlalchemy[asyncio]>=2.0.28` and `greenlet>=3.0.3` (pre-built wheels exist on PyPI for `cp315-win_amd64`).

---

### Issue 04: Starlette 0.36+ Breaking Signature Change in `TemplateResponse`
* **Symptom:** `TypeError: cannot use 'tuple' as a dict key (unhashable type: 'dict')` and `GET /favicon.ico 404 Not Found`.
* **Root Cause:** Modern Starlette (`>= 0.36.0`) / FastAPI (`0.162.0`) changed the parameter ordering of `Jinja2Templates.TemplateResponse` to `(request: Request, name: str, context: dict)`. Passing positional arguments as `TemplateResponse("name.html", {"request": request, ...})` caused Starlette to interpret the template name as `request` and the dictionary as `name`.
* **Resolution (Commit `ef06ce7`):**
  - Refactored all route handlers across [catalog_router.py](file:///C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore/app/web/catalog_router.py), [cart_router.py](file:///C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore/app/web/cart_router.py), and [account_router.py](file:///C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore/app/web/account_router.py) to use explicit keyword arguments:
    ```python
    return templates.TemplateResponse(request=request, name="...", context={...})
    ```
  - Added a dedicated 204 handler for `/favicon.ico` in [app/main.py](file:///C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore/app/main.py).

---

### Issue 05: Cart Page CSS Float Collapse & Footer Misalignment
* **Symptom:** In the shopping cart view, the **"Powered by iBATIS"** footer box floated up into the right-hand side of the page, overlapping the cart table and showing dark body background below.
* **Root Cause:**
  1. Legacy [jpetstore.css](file:///C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore/app/static/css/jpetstore.css) styles `#Cart` as `float: left; width: 69.99%;` and `#PoweredBy` as `float: left; width: 30%;`.
  2. Because floats inside `#Content` were not cleared, `#Content` collapsed to 0px computed height, allowing the `#PoweredBy` float to flow into the remaining 30% horizontal space next to `#Cart`.
* **Resolution (Commit `80f3847`):**
  - Added container clearfix rules (`clear: both; overflow: hidden;`) to `#Header`, `#Content`, and `#Footer` in [app/templates/common/base.html](file:///C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore/app/templates/common/base.html).
  - Configured `#Cart` to span `width: 100% !important; float: none !important;` with centered table layout.
  - Added `<div id="Separator">&nbsp;</div>` at the bottom of [app/templates/cart/cart.html](file:///C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore/app/templates/cart/cart.html) and [base.html](file:///C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore/app/templates/common/base.html).

---

### Issue 06: Async SQLAlchemy `MissingGreenlet` During Order View
* **Symptom:** `GET /order/viewOrder/1000 500 Internal Server Error`: `sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_() here. Was IO attempted in an unexpected place?`
* **Root Cause:** Inside [app/templates/order/view_order.html](file:///C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore/app/templates/order/view_order.html), the template accessed `line_item.item_rel.product_rel.name`. Because `product_rel` was not eagerly loaded during the initial query, SQLAlchemy attempted a synchronous lazy-load I/O operation inside Jinja2 template rendering, which is forbidden in async SQLAlchemy sessions.
* **Resolution (Commit `ca9596b`):**
  - Added `lazy="selectin"` to `LineItem.item_rel`, `Item.product_rel`, `Order.line_items`, and `Order.statuses` in [app/models/order.py](file:///C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore/app/models/order.py) and [app/models/catalog.py](file:///C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore/app/models/catalog.py).
  - Configured deep eager loading in [app/repositories/order_repository.py](file:///C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore/app/repositories/order_repository.py):
    ```python
    selectinload(Order.statuses),
    selectinload(Order.line_items)
        .selectinload(LineItem.item_rel)
        .selectinload(Item.product_rel)
    ```
  - Added defensive null checks in [app/templates/order/view_order.html](file:///C:/Angappan/SourceCode/TalentGigs/haiintel/jpetstore/app/templates/order/view_order.html).
