import logging
import random
from datetime import datetime, timedelta
import json
import re
import time
from django.db.models import Q
from asgiref.sync import sync_to_async
from django.dispatch import receiver
from django.db.models.signals import pre_save
from rest_framework.decorators import api_view
from API.models import Token, Users, UserInfo, Messages, Tariffs, FBids, Results, Codes, Bill, Diary
from django.http import JsonResponse
from API.formulas import formula1, formula2, formula3, formula4, get_recommendation, get_percent
import binascii
import os
from Backend.settings import cards
import filetype


def generate_key(length=20):
    return binascii.hexlify(os.urandom(length)).decode()


def verify_code(code, transaction_id):
    return True


def send_code(phone):
    transaction_id = "aaa"
    return transaction_id


def get_images(request):
    images = {}
    vertical = []
    horizontal = []
    protocol = 'https' if request.is_secure() else 'http'
    host = f'{protocol}://{request.get_host()}'
    for key, card in cards.items():
        if os.path.isfile(f'media/test_images/vertical/{key}.jpg'):
            vertical.append({
                "image_id": int(key),
                "title": card.get('name', ''),
                "image": f'{host}/media/test_images/vertical/{key}.jpg'
            })
        if os.path.isfile(f'media/test_images/horizontal/{key}.jpg'):
            horizontal.append({
                "image_id": int(key),
                "title": card.get('name', ''),
                "image": f'{host}/media/test_images/horizontal/{key}.jpg'
            })
    random.shuffle(vertical)
    random.shuffle(horizontal)
    images['vertical'] = vertical
    images['horizontal'] = horizontal
    return images


def select_card(data):
    result = []
    for key in data:
        result.append(cards.get(f"{key}", {}))

    return result


def repeats(data):
    temp = []
    for item in data:
        if item in temp:
            return True
        temp.append(item)
    return False


@sync_to_async
@api_view(["POST"])
def login(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['phone']
    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    phone = body.get('phone', '')

    if not re.match("^\\+?\\d{1,4}?[-.\\s]?\\(?\\d{1,3}?\\)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}$",
                    phone):
        return JsonResponse(
            {"success": 0, "error": f"The phone is incorrect"})

    phone = re.sub(r'\D', '', phone)

    codeObj = Codes.objects.filter(phone=phone)
    code = '1234'

    if codeObj:
        codeObj = codeObj.first()
        if datetime.utcnow().timestamp() - codeObj.update_time.timestamp() < 60:
            delta = (datetime.utcnow().timestamp() - codeObj.update_time.timestamp())
            return JsonResponse(
                {"success": 0,
                 "error": f"Wait {60 - int(delta)} seconds for next request"})
        else:
            codeObj.code = code
            codeObj.save()
    else:
        Codes.objects.create(phone=phone, code=code)

    return JsonResponse({"success": 1, "action": "check_code"})


@sync_to_async
@api_view(["POST"])
def logout(request):
    token = request.headers.get('token', '')

    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})
    tokenObj.first().delete()

    return JsonResponse({"success": 1, "action": "Logout"})


@sync_to_async
@api_view(["POST"])
def check_code(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['code', 'phone']
    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    phone = body.get('phone')
    code = body.get('code')

    if not re.match("^\\+?\\d{1,4}?[-.\\s]?\\(?\\d{1,3}?\\)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}$",
                    phone):
        return JsonResponse(
            {"success": 0, "error": f"The phone is incorrect"})

    phone = re.sub(r'\D', '', phone)

    codeObj = Codes.objects.filter(phone=phone)
    if not codeObj:
        return JsonResponse({"success": 0, "error": "Phone not found"})

    codeObj = codeObj.first()
    if code != codeObj.code:
        return JsonResponse({"success": 0, "error": "Incorrect code"})
    codeObj.delete()

    user, created = Users.objects.get_or_create(number=phone)

    token = generate_key(32)
    Token.objects.create(user=user, token=token)

    if not UserInfo.objects.filter(user=user):
        return JsonResponse({"success": 1, "action": "register", "token": token})

    return JsonResponse({"success": 1, "action": "login", "token": token})


@sync_to_async
@api_view(["POST"])
def register(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['name', 'surname', 'height', 'weight', 'age', 'lang']
    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    try:
        age = int(body.get('age'))
        weight = float(body.get('weight'))
        height = int(body.get('height'))
        surname = body.get('surname').strip()
        name = body.get('name').strip()
        lang = body.get('lang').strip()
        if age < 0:
            raise Exception('Age must be >= 0')
        if weight < 0:
            raise Exception('Weight must be >= 0')
        if height < 0:
            raise Exception('Height must be >= 0')
        if not name:
            raise Exception('Name is empty')
        if not surname:
            raise Exception('Surname is empty')
        if not lang:
            raise Exception('Lang is empty')
    except Exception as e:
        return JsonResponse({"success": 0, "error": str(e)})

    user = tokenObj.first().user
    userObj = UserInfo.objects.filter(user=user)
    if not userObj:
        UserInfo.objects.create(user=user, weight=weight, age=age, height=height, name=name, surname=surname, lang=lang)
    else:
        userObj = userObj.first()
        userObj.weight = weight
        userObj.age = age
        userObj.name = name
        userObj.surname = surname
        userObj.height = height
        userObj.lang = lang
        userObj.save()

    return JsonResponse({"success": 1})


@sync_to_async
@api_view(["POST"])
def get_me(request):
    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    data = {}
    user = tokenObj.first().user
    user_info = UserInfo.objects.filter(user=user)
    if user_info:
        user_info = user_info.first()
        data["name"] = user_info.name
        data["surname"] = user_info.surname
        data["height"] = user_info.height
        data["weight"] = user_info.weight
        data["age"] = user_info.age
        data["lang"] = user_info.lang

    data["phone"] = str(user)
    data["subscription_end"] = time.mktime(user.subscription_end.timetuple())

    return JsonResponse({"success": 1, "data": data})


@sync_to_async
@api_view(["POST"])
def get_products(request):
    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    data = []
    for tariff in Tariffs.objects.all():
        data.append({
            'id': tariff.pk,
            'title': tariff.title,
            'price': tariff.price,
            'currency': tariff.currency,
            'description': tariff.description,
        })

    return JsonResponse({"success": 1, "data": data})


@sync_to_async
@api_view(["POST"])
def get_test(request):
    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    data = get_images(request)

    return JsonResponse({"success": 1, "data": data})


@sync_to_async
@api_view(["POST"])
def set_fbid(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['fbid']

    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    FBids.objects.get_or_create(fBid=body.get('fbid', ''), token=tokenObj.first())

    return JsonResponse({"success": 1})


@sync_to_async
@api_view(["POST"])
def set_test(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['data']

    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    data = body.get('data')
    if type(data) != list or len(data) != 5 or repeats(data):
        return JsonResponse({"success": 0, "error": "Incorrect data"})

    try:
        if type(data) != list:
            raise Exception('Data type must be a list')
        if len(data) != 5:
            raise Exception('Data must include 5 elements')
        for i, value in enumerate(data):
            if not f"{value}".strip().isdigit():
                raise Exception('Data elements must be of type int')
            data[i] = int(f"{value}".strip())
        for value in data:
            if value > 49 or value < 1:
                raise Exception('Data elements must be between 1 and 49')
    except Exception as e:
        return JsonResponse({"success": 0, "error": f"Incorrect data: ({e})"})

    userObj = tokenObj.first().user

    selected_cards = select_card(data)

    recommendation = get_recommendation(selected_cards, userObj.lang)

    text = "Вы выбрали репродукции картин Мироток:\n"
    text += "\n".join([f"• {x.get('id', '')}.{x.get('name', '')}" for x in selected_cards])
    text += "\nОписание картин в таблице...\nАвтор живописных картин Бендицкий Игорь Эдуардович | BENDITSKIY IGOR"

    texts = [text]
    images = []

    f1_text = formula1(selected_cards)
    f2_text = formula2(selected_cards)

    texts.append(f"Мотивационно-образная формула:\n{f1_text}")
    texts.append(f"Баланс энергоемкости: {f2_text}%")
    texts.append(f"Баланс кислотно-щелочной среды: {round(get_percent(f2_text) * 1000) / 1000}pH")

    resultObj = Results.objects.create(percent=int(f2_text), user=userObj)

    f3_image, f3_text = formula3(selected_cards)
    f4_image, f4_text = formula4(selected_cards)

    texts.append(f"Остаточные эмоционально-образные блоки:\n{f3_text}")
    texts.append(f4_text)

    protocol = 'https' if request.is_secure() else 'http'
    host = f'{protocol}://{request.get_host()}'

    images.append(f"{host}/{f3_image}")
    images.append(f"{host}/{f4_image}")
    images.append(f"{host}/media/table.png")

    results = []
    try:
        for result in Results.objects.filter(user=userObj).order_by('-id')[:30]:
            results.append({
                "time": int(result.create_time.timestamp()),
                "result": result.percent,
                "resultPh": round(get_percent(result.percent) * 1000) / 1000
            })
    except Exception as e:
        return JsonResponse({"success": 0, "error": f"{e}"})

    data = {
        "text": texts,
        "images": images,
        "results": results,
        "recommendation": recommendation
    }

    resultObj.result = data
    resultObj.save()

    return JsonResponse({"success": 1, "data": data})


@sync_to_async
@api_view(["POST"])
def get_main(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['from', 'to']

    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    user = tokenObj.first().user

    data = {}
    messages = []
    try:
        for result in Results.objects.filter(user=user,
                                             create_time__range=[f"{body.get('from')}", f"{body.get('to')}"]):
            results = data.setdefault(f"{result.create_time.date()}", [])
            results.append(result.percent)
        for message in Messages.objects.filter(Q(user=user) | Q(private=False)).order_by('-id')[: 3]:
            messages.append({
                "id": message.id,
                "title": message.title,
                "text": message.text,
                "private": message.private,
                "time": int(message.create_time.timestamp()),
            })
    except Exception as e:
        return JsonResponse({"success": 0, "error": f"{e}"})

    return JsonResponse({
        "success": 1,
        "data": data,
        "messages": messages
    })


@sync_to_async
@api_view(["POST"])
def get_results(request):
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

    user = tokenObj.first().user

    data = []
    try:
        for result in Results.objects.filter(user=user).order_by('-id')[offset: limit + offset]:
            res = {
                "result_id": result.id,
                "percent": result.percent,
                "percentPh": round(get_percent(result.percent) * 1000) / 1000
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
def get_result(request):
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

    userObj = tokenObj.first().user

    try:
        result_id = int(body.get('result_id'))
    except:
        return JsonResponse({"success": 0, "error": "Incorrect data"})

    resultObj = Results.objects.filter(id=result_id, user=userObj)
    if not resultObj:
        return JsonResponse({"success": 0, "error": "Result not found"})

    result = resultObj.first()
    data = {
        "percent": result.percent,
        "result": result.result,
        "resultPh": round(get_percent(result.percent) * 1000) / 1000,
        "time": int(result.create_time.timestamp()),
    }
    return JsonResponse({"success": 1, "data": data})


@sync_to_async
@api_view(["POST"])
def buy(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['product_id']

    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    try:
        product_id = int(body.get('product_id'))
    except:
        return JsonResponse({"success": 0, "error": "Product_id must be of type int"})

    tokenObj = tokenObj.first()
    product = Tariffs.objects.filter(id=product_id)
    if not product:
        return JsonResponse({"success": 0, "error": "Product not found"})

    product = product.first()
    Bill.objects.create(user=tokenObj.user, product=product, amount=product.price)
    # toDo: buy product

    return JsonResponse({"success": 1, "action": "buyInApp"})


@sync_to_async
@api_view(["POST"])
def validate_buy(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['transaction_id']

    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    if type(body.get('transaction_id')) != str:
        return JsonResponse({"success": 0, "error": "Transaction_id must be of type string"})

    user = tokenObj.first().user

    # toDo: check transaction

    return JsonResponse({"success": 1, "subscription_end": f"{user.subscription_end}"})


@sync_to_async
@api_view(["POST"])
def validate_buy(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['transaction_id']

    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    if type(body.get('transaction_id')) != str:
        return JsonResponse({"success": 0, "error": "Transaction_id must be of type string"})

    user = tokenObj.first().user

    # toDo: check transaction

    return JsonResponse({"success": 1, "subscription_end": f"{user.subscription_end}"})


@sync_to_async
@api_view(["POST"])
def validate_buy(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['transaction_id']

    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    if type(body.get('transaction_id')) != str:
        return JsonResponse({"success": 0, "error": "Transaction_id must be of type string"})

    user = tokenObj.first().user

    # toDo: check transaction

    return JsonResponse({"success": 1, "subscription_end": f"{user.subscription_end}"})


@sync_to_async
@api_view(["POST"])
def add_diary(request):
    body = json.loads(request.body.decode())
    necessary_keys = ['text', 'type']

    for key in necessary_keys:
        if key not in body:
            return JsonResponse(
                {"success": 0, "error": f"The request must contain the following parameters: {necessary_keys}"})

    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    diary_type = body.get('type')
    text = f"{body.get('text')}"

    if type(diary_type) != int:
        return JsonResponse({"success": 0, "error": "Type must be of type int"})
    if diary_type > 4 or diary_type < 0:
        return JsonResponse({"success": 0, "error": "Type must be in range from 0 to 3"})

    if not text.strip():
        return JsonResponse({"success": 0, "error": "Text is empty"})

    user = tokenObj.first().user

    Diary.objects.create(user=user, text=text, type=diary_type)

    return JsonResponse({"success": 1})


@sync_to_async
@api_view(["POST"])
def get_my_diary(request):
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

    user = tokenObj.first().user

    data = []
    try:
        for diary in Diary.objects.filter(user=user).order_by('-id')[offset: limit + offset]:
            data.append({
                "type": diary.type,
                "text": diary.text,
                "time": int(diary.create_time.timestamp())
            })
    except Exception as e:
        return JsonResponse({"success": 0, "error": f"{e}"})

    return JsonResponse({"success": 1, "diary": data})


@sync_to_async
@api_view(["POST"])
def set_avatar(request):
    body = request.body

    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})
    if not body:
        return JsonResponse({"success": 0, "error": "Body is empty"})

    supported_types = ['png', 'jpg', 'jpeg']

    file = filetype.guess(body)

    if not file:
        return JsonResponse({"success": 0, "error": "Incorrect file"})

    if file.extension not in supported_types:
        return JsonResponse({"success": 0, "error": f"Incorrect extension. Supported extension: {supported_types}"})

    with open(f'media/avatars/{tokenObj.first().user.id}.jpg', 'wb') as photo:
        photo.write(body)
    return JsonResponse({"success": 1})


@sync_to_async
@api_view(["POST"])
def get_avatar(request):
    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})

    path = f'media/avatars/{tokenObj.first().user.id}.jpg'
    protocol = 'https' if request.is_secure() else 'http'
    host = f'{protocol}://{request.get_host()}'

    if os.path.exists(path):
        return JsonResponse({"success": 1, "avatar": f"{host}/{path}"})
    return JsonResponse({"success": 1, "avatar": f"{host}/media/avatars/user.png"})


@sync_to_async
@api_view(["POST"])
def logout(request):
    token = request.headers.get('token', '')
    tokenObj = Token.objects.filter(token=token)
    if not tokenObj:
        return JsonResponse({"success": 0, "error": "Token not found"})
    try:
        fbid = FBids.objects.filter(token=tokenObj)
        if fbid:
            fbid.first().delete()

        tokenObj.delete()
    except Exception as e:
        return JsonResponse({"success": 0, "error": str(e)})
    return JsonResponse({"success": 1})


@receiver(pre_save, sender=Bill)
def my_callback(sender, instance, *args, **kwargs):
    current_bill = Bill.objects.filter(pk=instance.pk)
    if current_bill:
        current_bill = current_bill.first()
        if not current_bill.status and instance.status:
            user = instance.user
            if user:
                user.subscription_end = max(user.subscription_end, datetime.today().date()) + timedelta(
                    days=instance.product.days)
                user.save()
