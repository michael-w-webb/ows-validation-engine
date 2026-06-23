from fastapi import (
    APIRouter,
    Request
)

from fastapi.responses import (
    HTMLResponse
)

import logging

from api.dependencies import (

    templates,

    workbook_definition_repository,

    validation_run_repository
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# Workbook Definition Builder Landing Page
# ============================================

@router.get("/workbook-definitions/new",
    response_class=HTMLResponse
)
async def home(
    request: Request
):

    logger.info(
        "Loading workbook definition builder"
    )

    return templates.TemplateResponse(
        request=request,
        name=(
            "workbook_definitions/"
            "new_definition.html"
        ),
        context={
            "request": request
        }
    )


# ============================================
# Registry / Operations Dashboard
# ============================================

@router.get(
    "/",
    response_class=HTMLResponse
)
async def workbook_definitions_home(
    request: Request
):

    logger.info(
        (
            "Loading workbook definition "
            "registry dashboard"
        )
    )

    queued = (

        request.query_params.get(
            "queued"
        ) == "true"
    )

    definitions = (
        workbook_definition_repository
        .list_definitions()
    )

    active_runs = (
        validation_run_repository
        .list_active_runs()
    )

    completed_runs = (
        validation_run_repository
        .list_completed_runs()
    )

    return templates.TemplateResponse(
        request=request,
        name="home/registry_home.html",
        context={

            "request": request,

            "queued": queued,

            "workbook_definitions":
                definitions,

            "active_runs":
                active_runs,

            "completed_runs":
                completed_runs
        }
    )