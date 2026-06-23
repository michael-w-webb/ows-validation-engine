# ============================================
# Workbook Definition Builder Routes
# ============================================
#
# This router manages the complete draft
# workbook-definition-building workflow.
#
# Responsibilities:
#
# 1. Create temporary WorkbookSession objects
#    from uploaded Excel workbooks.
#
# 2. Guide users through the multi-step
#    schema construction process:
#
#       Upload Workbook
#           ↓
#       Select Sheets
#           ↓
#       Configure Linking Columns
#           ↓
#       Generate Canonical Definitions
#           ↓
#       Configure Fields
#           ↓
#       Preview Workbook Definition
#
# 3. Coordinate UI rendering using Jinja2
#    templates for each workflow stage.
#
# 4. Delegate workbook/session mutation logic
#    to ParserService and related services.
#
# 5. Compile draft WorkbookSession state into
#    validation-engine-native workbook
#    definition objects for preview.
#
# ============================================

from fastapi import (
    APIRouter,
    Request,
    Form,
    File,
    UploadFile
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from api.services.field_configuration import (
    field_is_configured
)

from api.services.workbook_definition_builder import(
    WorkbookDefinitionBuilder
)

import logging
from api.dependencies import templates, parser_service, workbook_definition_repository

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================
# Create Workbook Definition Session
# ============================================

@router.post(
    "/workbook-definitions/new",
    response_class=HTMLResponse
)
async def create_workbook_definition(
    request: Request,
    workbook_name: str = Form(...),
    format_name: str = Form(...),
    is_multi_sheet: bool = Form(False),
    workbook_file: UploadFile = File(...),
    header_row: int = Form(1)
):

    logger.info(
        (
            "Creating workbook definition "
            "session for workbook %s"
        ),
        workbook_file.filename
    )

    try:

        contents = await workbook_file.read()

        session = (
            parser_service.create_session(
                contents=contents,
                filename=workbook_file.filename,
                workbook_name=workbook_name,
                format_name=format_name,
                is_multi_sheet=is_multi_sheet,
                header_row=header_row
            )
        )

        logger.info(
            (
                "Workbook definition "
                "session created successfully"
            )
        )

        return RedirectResponse(
            url=(
                f"/draft/"
                f"{session.resource_id}"
                f"/sheets"
            ),
            status_code=303
        )

    except Exception as e:

        logger.exception(
            (
                "Failed creating workbook "
                "definition session"
            )
        )

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "error": str(e)
            }
        )



# ============================================
# Select Sheets Page
# ============================================

@router.get(
    "/draft/{resource_id}/sheets",
    response_class=HTMLResponse
)
async def select_sheets_page(
    request: Request,
    resource_id: str
):

    logger.info(
        (
            "Loading sheet selection "
            "page for session %s"
        ),
        resource_id
    )

    try:

        session = (
            parser_service.load_session(
                resource_id
            )
        )

        return templates.TemplateResponse(
            request=request,
            name=(
                "workbook_definitions/"
                "select_sheets.html"
            ),
            context={
                "request": request,
                "session": session
            }
        )

    except Exception as e:

        logger.exception(
            (
                "Failed loading sheet "
                "selection page"
            )
        )

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "error": str(e)
            }
        )


# ============================================
# Save Selected Sheets
# ============================================

@router.post(
    "/draft/{resource_id}/sheets",
    response_class=HTMLResponse
)
async def save_selected_sheets(
    request: Request,
    resource_id: str,
    selected_sheets: list[str] = Form(...)
):

    logger.info(
        (
            "Saving selected sheets "
            "for session %s"
        ),
        resource_id
    )

    try:

        session = (
            parser_service.update_selected_sheets(
                resource_id,
                selected_sheets
            )
        )

        return RedirectResponse(
            url=(
                f"/draft/"
                f"{resource_id}"
                f"/linking"
            ),
            status_code=303
        )

    except Exception as e:

        logger.exception(
            (
                "Failed saving selected "
                "sheets"
            )
        )

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "error": str(e)
            }
        )


# ============================================
# Adjust Sheet Header
# ============================================

@router.post(
    "/adjust-sheet-header"
)
async def adjust_sheet_header(
    request: Request,
    resource_id: str = Form(...),
    target_sheet: str = Form(...),
    header_row: int = Form(...)
):

    logger.info(
        (
            "Updating sheet header row "
            "for sheet %s to row %s"
        ),
        target_sheet,
        header_row
    )

    try:

        session = (
            parser_service.update_sheet_header(
                resource_id=resource_id,
                target_sheet=target_sheet,
                header_row=header_row
            )
        )

        logger.info(
            (
                "Updated sheet header "
                "successfully for sheet %s"
            ),
            target_sheet
        )

        safe_sheet = target_sheet.replace(" ", "-")

        return RedirectResponse(
            url=f"/draft/{resource_id}/sheets#sheet-{safe_sheet}",
            status_code=303
        )

    except FileNotFoundError:

        logger.exception(
            (
                "Failed updating sheet "
                "header for sheet %s"
            ),
            target_sheet
        )

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "error": (
                    "Session expired. "
                    "Please re-upload workbook."
                )
            }
        )

    except Exception as e:

        logger.exception(
            (
                "Failed updating sheet "
                "header for sheet %s"
            ),
            target_sheet
        )

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "error": str(e)
            }
        )

# ============================================
# Adjust Linking Rule
# ============================================

    
@router.get(
    "/draft/{resource_id}/linking",
    response_class=HTMLResponse
)
async def linking_page(
    request: Request,
    resource_id: str
):

    logger.info(
        (
            "Loading linking page "
            "for session %s"
        ),
        resource_id
    )

    try:

        session = (
            parser_service.load_session(
                resource_id
            )
        )

        return templates.TemplateResponse(
            request=request,
            name=(
                "workbook_definitions/"
                "link_sheets.html"
            ),
            context={
                "request": request,
                "session": session
            }
        )

    except Exception as e:

        logger.exception(
            "Failed loading linking page"
        )

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "error": str(e)
            }
        )

# ============================================
# Save Linking Rule
# ============================================

@router.post(
    "/draft/{resource_id}/linking",
    response_class=HTMLResponse
)
async def save_linking_rules(
    request: Request,
    resource_id: str
):

    logger.info(
        (
            "Saving linking rules "
            "for session %s"
        ),
        resource_id
    )

    try:

        session = (
            parser_service.load_session(
                resource_id
            )
        )

        form = await request.form()

        linking_rules = {}

        for sheet_name in (
            session.selected_sheets
        ):

            selected_columns = []

            for i in range(1, 6):

                value = form.get(
                    f"{sheet_name}_link_{i}"
                )

                if value:

                    selected_columns.append(
                        value
                    )

            linking_rules[
                sheet_name
            ] = selected_columns

        session = (
            parser_service.update_linking_rules(
                resource_id,
                linking_rules
            )
        )

        session = (
            parser_service.generate_canonical_definitions(
                session
            )
        )

        return RedirectResponse(
            url=(
                f"/draft/"
                f"{resource_id}"
                f"/fields_overview"
            ),
            status_code=303
        )

    except Exception as e:

        logger.exception(
            "Failed saving linking rules"
        )

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "error": str(e)
            }
        )
    

# ============================================
# Fields Overview Page
# ============================================

@router.get(
    "/draft/{resource_id}/fields_overview",
    response_class=HTMLResponse
)
async def fields_overview_page(
    request: Request,
    resource_id: str
):

    logger.info(
        (
            "Loading fields overview "
            "for session %s"
        ),
        resource_id
    )

    try:

        session = (
            parser_service.load_session(
                resource_id
            )
        )

        active_sheet = request.query_params.get(
            "sheet"
        )

        field_types = [
            "categorical",
            "fileSpecificCategorical",
            "identifier",
            "boolean",
            "dateTime",
            "zipCode",
            "stateID7",
            "ONETCode",
            "CIPCode",
            "hourlyWage",
            "hoursWorked",
            "NAICSCode"
        ]

        return templates.TemplateResponse(
            request=request,
            name=(
                "workbook_definitions/"
                "fields_overview.html"
            ),
            context={
                "request": request,
                "session": session,
                "field_types": field_types,
                "active_sheet": active_sheet
            }
        )

    except Exception as e:

        logger.exception(
            (
                "Failed loading fields "
                "overview"
            )
        )

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "error": str(e)
            }
        )
    
# ============================================
# Field Editor Page
# ============================================

@router.get(
    "/draft/{resource_id}/fields_overview/{field_id}",
    response_class=HTMLResponse
)
async def field_editor_page(
    request: Request,
    resource_id: str,
    field_id: str
):

    logger.info(
        (
            "Loading field editor "
            "for session %s field %s"
        ),
        resource_id,
        field_id
    )

    try:

        session = (
            parser_service.load_session(
                resource_id
            )
        )

        for field in session.canonical_definitions:

            field["status"] = (
                "configured"
                if field_is_configured(field)
                else "unconfigured"
            )

        field = next(
            (
                field
                for field in session.canonical_definitions
                if field["field_id"] == field_id
            ),
            None
        )

        if field is None:

            raise ValueError(
                f"Field not found: {field_id}"
            )

        field_types = [
            "categorical",
            "fileSpecificCategorical",
            "identifier",
            "boolean",
            "dateTime",
            "zipCode",
            "stateID7",
            "ONETCode",
            "CIPCode",
            "hourlyWage",
            "hoursWorked",
            "NAICSCode"
        ]

        return templates.TemplateResponse(
            request=request,
            name=(
                "workbook_definitions/"
                "field_editor.html"
            ),
            context={
                "request": request,
                "session": session,
                "field": field,
                "field_id": field_id,
                "field_types": field_types
            }
        )

    except Exception as e:

        logger.exception(
            (
                "Failed loading field "
                "editor"
            )
        )

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "error": str(e)
            }
        )
    
# ============================================
# Save Field Editor
# ============================================

@router.post(
    "/draft/{resource_id}/fields_overview/{field_id}"
)
async def save_field_editor(
    request: Request,
    resource_id: str,
    field_id: str
):

    logger.info(
        (
            "Saving field editor "
            "for session %s field %s"
        ),
        resource_id,
        field_id
    )

    try:

        session = (
            parser_service.load_session(
                resource_id
            )
        )

        field = next(
            (
                field
                for field in session.canonical_definitions
                if field["field_id"] == field_id
            ),
            None
        )

        if field is None:

            raise ValueError(
                f"Field not found: {field_id}"
            )

        form = await request.form()

        field["canonical_name"] = (
            form.get(
                "canonical_name"
            )
        )

        field["column_type"] = (
            form.get(
                "column_type"
            )
        )

        field["required"] = (
            form.get(
                "required"
            ) == "on"
        )

        field["included"] = (
            form.get(
                "included"
            ) == "on"
        )

        accepted_response_text = (
            form.get(
                "accepted_responses"
            )
        )

        if accepted_response_text:

            field["accepted_responses"] = [

                line.strip()

                for line in (
                    accepted_response_text.splitlines()
                )

                if line.strip()
            ]

        else:

            field["accepted_responses"] = []


        field["status"] = (
            "configured"
            if field_is_configured(field)
            else "unconfigured"
        )

        parser_service.persist_session(
            session
        )

        return RedirectResponse(
            url=(
                f"/draft/"
                f"{resource_id}"
                f"/fields_overview/"
                f"{field_id}"
            ),
            status_code=303
        )

    except Exception as e:

        logger.exception(
            (
                "Failed saving field "
                "editor"
            )
        )

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "request": request,
                "error": str(e)
            }
        )
    
@router.get(
    "/draft/{resource_id}/preview",
    response_class=HTMLResponse
)
async def preview_definition_page(
    request: Request,
    resource_id: str
):

    session = parser_service.load_session(
        resource_id
    )

    builder = WorkbookDefinitionBuilder()

    session = (
        builder.build_workbook_definition(
            session
        )
    )

    parser_service.persist_session(session)

    return templates.TemplateResponse(
        request=request,
        name=(
            "workbook_definitions/"
            "preview_definition.html"
        ),
        context={
            "request": request, 
            "session": session,
            "workbook_definition":
                session.workbook_definition
        }
    )


# ============================================
# Finalize Draft Workbook Definition
# ============================================

@router.post(
    "/draft/{resource_id}/finalize"
)
async def finalize(
    resource_id: str
):
    
    session = parser_service.load_session(
            resource_id
        )
    
    builder = WorkbookDefinitionBuilder()

    session = (
        builder.build_workbook_definition(
            session
        )
    )

    workbook_definition_repository.save_definition(
        workbook_name=session.workbook_name,
        format_name=session.format_name,
        workbook_definition=(
            session.workbook_definition
        )
    )

    return RedirectResponse(
        url="/",
        status_code=303
    )

