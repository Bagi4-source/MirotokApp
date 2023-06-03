from datetime import datetime, timedelta
import json
import re
import time

from asgiref.sync import sync_to_async
from django.dispatch import receiver
from django.db.models.signals import pre_save
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from API.models import Token, Users, UserInfo, Messages, Tariffs, FBids, Results, Codes, Bill, Diary
from django.http import JsonResponse
from API.formulas import formula1, formula2, formula3, formula4
import binascii
import os
from Backend.settings import cards


@sync_to_async
@api_view(["POST"])
def get_users(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['offset', 'limit']
    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')

    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    tokenObj = tokenObj.first()
    if tokenObj.user.role != 1:
        return JsonResponse({"success": 0, "error": "Permission issue"})

    try:
        offset = int(body.get('offset'))
        limit = int(body.get('limit'))
        if limit < 0:
            raise Exception('Limit must be >= 0')
        if offset < 0:
            raise Exception('Offset must be >= 0')
    except:
        return JsonResponse({"success": 0, "error": "Incorrect data"})

    users = []
    try:
        for user in UserInfo.objects.all().order_by('-id')[offset: limit + offset]:
            users.append({
                "id": user.user.id,
                "name": user.name,
                "surname": user.surname,
                "height": user.height,
                "weight": user.weight,
                "age": user.age,
            })
    except Exception as e:
        return JsonResponse({"success": 0, "error": f"{e}"})

    return JsonResponse({"success": 1, "users": users})


@sync_to_async
@api_view(["POST"])
def get_user(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['user_id']
    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')

    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    tokenObj = tokenObj.first()
    if tokenObj.user.role != 1:
        return JsonResponse({"success": 0, "error": "Permission issue"})

    try:
        user_id = int(body.get('user_id'))
    except:
        return JsonResponse({"success": 0, "error": "Incorrect user_id"})

    userData = {}
    try:
        user = UserInfo.objects.filter(id=user_id)
        if user:
            user = user.first()
            userData = {
                "id": user.user.id,
                "name": user.name,
                "surname": user.surname,
                "height": user.height,
                "weight": user.weight,
                "age": user.age,
            }
    except Exception as e:
        return JsonResponse({"success": 0, "error": f"{e}"})

    return JsonResponse({"success": 1, "user": userData})


@sync_to_async
@api_view(["POST"])
def send_messages_all(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['text']
    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')

    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    tokenObj = tokenObj.first()
    if tokenObj.user.role != 1:
        return JsonResponse({"success": 0, "error": "Permission issue"})

    text = f"{body.get('text')}"
    if text.strip():
        Messages.objects.create(text=text)
    else:
        return JsonResponse({"success": 0, "error": "Text is empty"})

    return JsonResponse({"success": 1})


@sync_to_async
@api_view(["POST"])
def send_message(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['text']
    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')

    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    tokenObj = tokenObj.first()
    if tokenObj.user.role != 1:
        return JsonResponse({"success": 0, "error": "Permission issue"})

    try:
        user_id = int(body.get('user_id'))
    except:
        return JsonResponse({"success": 0, "error": "Incorrect user_id"})

    userObj = Users.objects.filter(id=user_id)
    if not userObj:
        return JsonResponse({"success": 0, "error": "User not found"})

    text = f"{body.get('text')}"
    if text.strip():
        Messages.objects.create(text=text, private=True, user=userObj.first())
    else:
        return JsonResponse({"success": 0, "error": "Text is empty"})

    return JsonResponse({"success": 1})


@sync_to_async
@api_view(["POST"])
def get_all_messages(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['offset', 'limit']
    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')

    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    tokenObj = tokenObj.first()
    if tokenObj.user.role != 1:
        return JsonResponse({"success": 0, "error": "Permission issue"})

    try:
        offset = int(body.get('offset'))
        limit = int(body.get('limit'))
        if limit < 0:
            raise Exception('Limit must be >= 0')
        if offset < 0:
            raise Exception('Offset must be >= 0')
    except:
        return JsonResponse({"success": 0, "error": "Incorrect data"})

    messages = []
    try:
        for message in Messages.objects.all().order_by('-id')[offset: limit + offset]:
            messages.append({
                "id": message.id,
                "title": message.title,
                "text": message.text,
                "userId": message.user.id if message.user else None,
                "private": message.private,
                "time": int(message.create_time.timestamp()),
            })
    except Exception as e:
        return JsonResponse({"success": 0, "error": f"{e}"})

    return JsonResponse({"success": 1, "messages": messages})


@sync_to_async
@api_view(["POST"])
def get_user_results(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['offset', 'limit', 'user_id']
    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')

    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    tokenObj = tokenObj.first()
    if tokenObj.user.role != 1:
        return JsonResponse({"success": 0, "error": "Permission issue"})

    try:
        offset = int(body.get('offset'))
        limit = int(body.get('limit'))
        if limit < 0:
            raise Exception('Limit must be >= 0')
        if offset < 0:
            raise Exception('Offset must be >= 0')
    except:
        return JsonResponse({"success": 0, "error": "Incorrect data"})

    try:
        user_id = int(body.get('user_id'))
    except:
        return JsonResponse({"success": 0, "error": "Incorrect user_id"})

    userObj = Users.objects.filter(id=user_id)
    if not userObj:
        return JsonResponse({"success": 0, "error": "User not found"})
    userObj = userObj.first()

    data = []
    try:
        for result in Results.objects.filter(user=userObj).order_by('-id')[offset: limit + offset]:
            res = {
                "percent": result.percent
            }
            if body.get('extra', 0):
                res["result"] = result.result
            data.append({
                "time": int(result.create_time.timestamp()),
                "result": res
            })
    except Exception as e:
        return JsonResponse({"success": 0, "error": f"{e}"})

    return JsonResponse({"success": 1, "data": data})

@sync_to_async
@api_view(["POST"])
def get_user_result(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['result_id']
    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')

    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    tokenObj = tokenObj.first()
    if tokenObj.user.role != 1:
        return JsonResponse({"success": 0, "error": "Permission issue"})

    try:
        result_id = int(body.get('result_id'))
    except:
        return JsonResponse({"success": 0, "error": "Incorrect data"})

    resultObj = Results.objects.filter(id=result_id)
    if not resultObj:
        return JsonResponse({"success": 0, "error": "Result not found"})

    result = resultObj.first()
    data = {
        "percent": result.percent,
        "result": result.result,
        "time": int(result.create_time.timestamp()),
    }
    return JsonResponse({"success": 1, "data": data})

@sync_to_async
@api_view(["POST"])
def get_user_diary(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['offset', 'limit', 'user_id']

    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    try:
        offset = int(body.get('offset'))
        limit = int(body.get('limit'))
        if limit < 0:
            raise Exception('Limit must be >= 0')
        if offset < 0:
            raise Exception('Offset must be >= 0')
    except:
        return JsonResponse({"success": 0, "error": "Incorrect data"})

    try:
        user_id = int(body.get('user_id'))
    except:
        return JsonResponse({"success": 0, "error": "Incorrect user_id"})

    userObj = Users.objects.filter(id=user_id)
    if not userObj:
        return JsonResponse({"success": 0, "error": "User not found"})
    userObj = userObj.first()

    data = []
    try:
        for diary in Diary.objects.filter(user=userObj).order_by('-id')[offset: limit + offset]:
            data.append({
                "type": diary.type,
                "text": diary.text,
                "time": int(diary.create_time.timestamp())
            })
    except Exception as e:
        return JsonResponse({"success": 0, "error": f"{e}"})

    return JsonResponse({"success": 1, "diary": data})
