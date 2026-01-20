"""
学期模块 - 控制器
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.dependencies import AuthPermission
from app.core.exceptions import CustomException
from app.core.router_class import OperationLogRoute

from .service import SemesterService
from .schema import SemesterCreateSchema, SemesterUpdateSchema, SemesterQueryParam
from ..enums import SemesterTypeEnum, SemesterStatusEnum