from pathlib import Path
import shutil
import logging

from fastapi import (
    APIRouter,
    Request,
    UploadFile,
    BackgroundTasks,
    File,
    Form
)

from fastapi.responses import (
    HTMLResponse,
    FileResponse,
    RedirectResponse
)

from api.dependencies import (
    templates,
    workbook_definition_repository,
    validation_run_repository,
    validation_service
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================
# Validation Launch Page
# ============================================

@router.get(
    "/validate/{workbook_definition_id}",
    response_class=HTMLResponse
)
async def validation_page(
    request: Request,
    workbook_definition_id: str
):

    logger.info(
        (
            "Loading validation page "
            "for workbook definition %s"
        ),
        workbook_definition_id
    )

    definition_record = (
        workbook_definition_repository
        .load_definition(
            workbook_definition_id
        )
    )

    return templates.TemplateResponse(
        request=request,
        name=(
            "validation_runs/"
            "run_validation.html"
        ),
        context={

            "request": request,

            "definition": (
                definition_record
            )
        }
    )


# ============================================
# Run Validation
# ============================================
@router.post(
    "/validate/{workbook_definition_id}",
    response_class=HTMLResponse
)
async def run_validation(
    request: Request,

    workbook_definition_id: str,

    background_tasks: BackgroundTasks,

    org: str = Form(...),

    target_period: str = Form(...),

    uploaded_file: UploadFile = File(...),

):

    logger.info(
        (
            "Starting validation POST "
            "for workbook definition %s"
        ),
        workbook_definition_id
    )

    definition_record = (
        workbook_definition_repository
        .load_definition(
            workbook_definition_id
        )
    )

    workbook_definition = (
        definition_record[
            "workbook_definition"
        ]
    )

    temp_upload_dir = Path(
        "temp_uploads"
    )

    temp_upload_dir.mkdir(
        exist_ok=True
    )

    logger.info(
        "Resolved upload directory: %s",
        temp_upload_dir.resolve()
    )

    uploaded_file_path = (
        temp_upload_dir
        / uploaded_file.filename
    )

    logger.info(
        (
            "Saving uploaded workbook "
            "to %s"
        ),
        uploaded_file_path
    )

    with open(
        uploaded_file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            uploaded_file.file,
            buffer
        )

    logger.info(
        "Running validation service"
    )

    validation_run_id = (

        validation_run_repository
        .create_run(

            workbook_definition_id=(
                workbook_definition_id
            ),

            workbook_name=(
                definition_record[
                    "workbook_name"
                ]
            ),

            format_name=(
                definition_record[
                    "format_name"
                ]
            ),

            org=org,

            target_period=(
                target_period
            ),

            uploaded_file_path=(
                uploaded_file_path
            )
        )
    )

    background_tasks.add_task(

        validation_service.run_validation,

        workbook_definition,
        
        validation_run_id,

        uploaded_file_path,

        org,

        target_period
    )

    logger.info(
        "Rendering validation results page"
    )

    return RedirectResponse(
        url="/?queued=true",
        status_code=303
    )

@router.get(
    "/validation-results/download"
)
async def download_validation_report(
    file_path: str
):

    logger.info(
        (
            "Downloading validation "
            "report %s"
        ),
        file_path
    )

    output_file = Path(
        file_path
    )

    return FileResponse(
        path=output_file,
        filename=output_file.name,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )