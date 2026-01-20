"""
学员模块 - 控制器
"""

import io
from typing import Optional

from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.base_schema import BatchSetAvailable
from app.core.dependencies import AuthPermission
from app.core.exceptions import CustomException
from app.core.router_class import OperationLogRoute

from .service import StudentService, ParentStudentService, AbilityAssessmentService
from .schema import (
    StudentCreateSchema,
    StudentUpdateSchema,
    StudentQueryParam,
    ParentStudentCreateSchema,
    AbilityAssessmentCreateSchema,
    AbilityAssessmentUpdateSchema,
    AbilityAssessmentQueryParam
)