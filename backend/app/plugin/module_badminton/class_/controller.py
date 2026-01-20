"""
class_模块 - 控制器
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from app.core.dependencies import AuthPermission
from app.core.exceptions import CustomException
from app.core.router_class import OperationLogRoute

from .schema import *
from .service import *

# class_模块路由器
Class_Router = APIRouter(
    route_class=OperationLogRoute,
    prefix="/class_",
    tags=["class_管理"]
)

@Class_Router.get("/semester/{semester_id}", summary="学期班级", description="获取指定学期的所有班级")
async def classes_by_semester(
    semester_id: int,
    auth: AuthSchema = Depends(AuthPermission(["module_badminton:class:list"]))
) -> JSONResponse:
    """学期班级"""
    result = await ClassService.get_by_semester_service(auth, semester_id)
    return SuccessResponse(data=result, msg="学期班级获取成功")


# ============================================================================
# 学期制课时结算系统 - 购买记录管理 API
# ============================================================================
