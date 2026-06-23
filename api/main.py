from api.core.logging_config import (
    configure_logging
)

configure_logging()

from fastapi import (
    FastAPI
)

from fastapi.staticfiles import (
    StaticFiles
)

from api.services.temp_storage import (
    cleanup_expired_files
)

from api.routes import (
    home,
    workbook_definition_builder,
    workbook_validator
)

import logging

from api.config import BASE_DIR
from api.dependencies import parser_service


# ============================================
# App Setup
# ============================================

logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(home.router)
app.include_router(workbook_definition_builder.router)
app.include_router(workbook_validator.router)

app.mount(
    "/static",
    StaticFiles(
        directory=str(BASE_DIR / "static")
    ),
    name="static"
)

# # ============================================
# # Startup Cleanup
# # ============================================

# # @app.on_event("startup")
# # async def startup_cleanup():

# #     logger.info(
# #         "Running startup cleanup"
# #     )

# #     cleanup_expired_files()

# #     logger.info(
# #         "Startup cleanup complete"
# #     )

# @app.on_event("startup")
# async def startup_cleanup():

#     logger.info(
#         "Skipping cleanup during development"
#     )
