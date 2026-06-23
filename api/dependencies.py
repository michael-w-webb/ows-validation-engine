from api.config import BASE_DIR, WB_DEF_DB_PATH, LOCAL_OUTPUT_DIRECTORY

from fastapi.templating import (
    Jinja2Templates
)

from api.services.workbook_parser.parser_service import (
    ParserService
)

from api.services.workbook_definition_repository import (
    WorkbookDefinitionRepository
)

from api.services.validation_run_repository import (
    ValidationRunRepository
)

from api.services.workbook_validation import (
    ValidationService
)

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

workbook_definition_repository = WorkbookDefinitionRepository(
        WB_DEF_DB_PATH
    )

validation_run_repository = ValidationRunRepository(
        WB_DEF_DB_PATH
    )

parser_service = ParserService()
validation_service = ValidationService(LOCAL_OUTPUT_DIRECTORY, validation_run_repository)