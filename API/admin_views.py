from datetime import datetime, timedelta
import json
import re
import time
from django.db.models import Q
from asgiref.sync import sync_to_async
from django.dispatch import receiver
from django.db.models.signals import pre_save
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from API.minioClient import MinioClient
from API.models import Token, Users, UserInfo, Messages, Tariffs, FBids, Results, Codes, Bill, Diary
from django.http import JsonResponse
from API.formulas import formula1, formula2, formula3, formula4, get_percent
import binascii
import os
from API.views import ROLES
from Backend.settings import cards

minio = MinioClient()


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

    search = str(body.get('search', '')).strip()
    if search:
        queryset = UserInfo.objects.filter(
            Q(name__icontains=search) | Q(surname__icontains=search) | Q(user__number__icontains=search)).order_by(
            '-id')[
                   offset: limit + offset]
    else:
        queryset = UserInfo.objects.all().order_by('-id')[offset: limit + offset]

    users = []
    try:
        for user in queryset:
            path = minio.get_url("avatars", f"user{user.user.id}.png")
            if not path:
                path = minio.get_url("avatars", f"user.png")
            users.append({
                "id": user.user.id,
                "phone": user.user.number,
                "name": user.name,
                "surname": user.surname,
                "height": user.height,
                "weight": user.weight,
                "age": user.age,
                "lang": user.lang,
                "subscription_end": time.mktime(user.user.subscription_end.timetuple()),
                "role": ROLES.get(f"{user.user.role}", "client"),
                "avatar": path
            })
    except Exception as e:
        return JsonResponse({"success": 0, "error": f"{e}"})

    return JsonResponse({"success": 1, "users": users, "total": UserInfo.objects.count()})


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
        user = UserInfo.objects.filter(user_id=user_id)
        if user:
            user = user.first()
            path = minio.get_url("avatars", f"user{user.user.id}.png")
            if not path:
                path = minio.get_url("avatars", f"user.png")
            userData = {
                "id": user.user.id,
                "phone": user.user.number,
                "name": user.name,
                "surname": user.surname,
                "height": user.height,
                "weight": user.weight,
                "age": user.age,
                "lang": user.lang,
                "subscription_end": time.mktime(user.user.subscription_end.timetuple()),
                "role": ROLES.get(f"{user.user.role}", "client"),
                "avatar": path
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

    tokenObj = tokenObj.first()
    if tokenObj.user.role != 1:
        queryset = Messages.objects.filter(Q(user=tokenObj.user) | Q(user=None)).order_by('-id')
        all_messages = queryset[offset: limit + offset]
        total = queryset.count()
    else:
        all_messages = Messages.objects.all().order_by('-id')[offset: limit + offset]
        total = Messages.objects.count()
    try:
        for message in all_messages:
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

    return JsonResponse({"success": 1, "messages": messages, "total": total})


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
                "result_id": result.id,
                "percent": result.percent,
                "resultPh": round(get_percent(result.percent) * 1000) / 1000,
            }
            if body.get('extra', 0):
                res["result"] = result.result
            data.append({
                "time": int(result.create_time.timestamp()),
                "result": res
            })
    except Exception as e:
        return JsonResponse({"success": 0, "error": f"{e}"})

    return JsonResponse({"success": 1, "data": data, "total": Results.objects.filter(user=userObj).count()})


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

    return JsonResponse({"success": 1, "diary": data, "total": Diary.objects.filter(user=userObj).count()})
