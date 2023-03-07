from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.response import Response

from celery_example.celery import app as celery_app

import celery_example
from task.tasks import calculate_metric
from celery.result import AsyncResult


# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.request import Request


@api_view(["PUT"])
def launch(request: Request, *args, **kwargs) -> HttpResponse:
    result = calculate_metric.delay()
    print(result.as_list())
    return JsonResponse(
        {
            "task_id": result.as_list()[-1]
        }
    )


@api_view(["GET"])
def get_result(request: Request, *args, **kwargs) -> HttpResponse:
    task_id = request.query_params.get('job_id')
    if not task_id:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            "detail": "job_id not found"
        })
    res = AsyncResult(task_id, app=celery_app)
    print(res.as_list())
    state = res.state
    if state == 'PENDING':
        return Response(status=status.HTTP_400_BAD_REQUEST, data={
            "detail": "invalid job_id"
        })
    return JsonResponse(
        {
            "status": state,
            "result": res.get() if state == "SUCCESS" else None
        }
    )
