from PIL import Image, ImageFont, ImageDraw
import os
import re
from datetime import datetime
import uuid

DIR = 'static/bp_masks'
ARROWS_DIR = 'static/arrows'


def get_time(str_time):
    str_time = str_time.split('.')[0]
    return datetime.fromisoformat(str_time)


def get_random_name(path, extension):
    while True:
        filename = str(uuid.uuid4())
        x = os.path.join(path, f"{filename}.{extension}")
        if not os.path.exists(x):
            return x


def generate_image(positive, negative):
    image = Image.open(os.path.join(DIR, 'bg.png'))
    for item in positive:
        path = os.path.join(os.path.join(DIR, 'pink'), f'{item.upper()}.png')
        if os.path.exists(path):
            item = Image.open(path)
            image.paste(item, mask=item)

    for item in negative:
        path = os.path.join(os.path.join(DIR, 'blue'), f'{item.upper()}.png')
        if os.path.exists(path):
            item = Image.open(path)
            image.paste(item, mask=item)

    bg = Image.open(os.path.join(DIR, 'bg2.png'))
    bg.paste(image)
    return bg


def get_recommendation(selected_cards, lang="ru"):
    langs = {
        "ru": "REC_RU"
    }
    recommendation = []
    key = langs.get(lang[:2], "REC_EN")
    for card in selected_cards:
        recommendation.append(card.get(key, ''))
    return recommendation


def bones_sum(selected_cards):
    bones = []
    for card in selected_cards:
        bones.extend([x for x in card.get('bones', []) if x not in bones])
    return bones


def get_degree(x):
    if x < 0:
        return f"{(abs(x) - 1) * 15}°"
    if x > 0:
        return f"{(x - 1) * 15}°"
    return '--'


def get_color(x):
    if x < 0:
        return (0, 163, 255)
    if x > 0:
        return (255, 153, 0)
    return (0, 0, 0)


def get_res_string(items, key):
    return f"{'ВП' if items[key] > 0 else 'НЗ' if items[key] < 0 else ''} {get_degree(items[key])}"


def get_percent(x):
    if x >= 19:
        return 7.35 - (x - 19) * 0.025
    if x <= -19:
        return 7.45 - (x + 19) * 0.025
    if x == 0:
        return 7.4
    return 7.4 + x * 0.05 / 19


def get_image(items):
    image = Image.open(os.path.join(ARROWS_DIR, 'bg.png'))
    for key, value in items.items():
        if value != 0:
            path = os.path.join(os.path.join(ARROWS_DIR, key), f'{value}.png')
            if os.path.exists(path):
                item = Image.open(path)
                image.paste(item, mask=item)
            if value > 0:
                path = os.path.join(os.path.join(ARROWS_DIR, key), f'0.png')
                if os.path.exists(path):
                    item = Image.open(path)
                    image.paste(item, mask=item)
            else:
                path = os.path.join(os.path.join(ARROWS_DIR, key), f'-0.png')
                if os.path.exists(path):
                    item = Image.open(path)
                    image.paste(item, mask=item)

    imageDraw = ImageDraw.Draw(image)
    font = ImageFont.truetype(os.path.join(ARROWS_DIR, 'Inter.ttf'), 34)
    font.set_variation_by_name('Bold')

    def drawText(position, k):
        imageDraw.text(position, get_res_string(items, k), font=font, align="center", fill=(45, 45, 45))

    drawText((330, 890), 'ФБ')
    drawText((455, 890), 'СМ')
    drawText((330, 940), 'ЛР')
    drawText((455, 940), 'ЗД')

    bg = Image.open(os.path.join(ARROWS_DIR, 'bg2.png'))
    bg.paste(image)
    return bg


def formula4(selected_cards):
    if len(selected_cards) != 5:
        return None
    positive = selected_cards[:3]
    negative = selected_cards[3:]

    result = {
        'ЛР': 0,
        'ЗД': 0,
        'СМ': 0,
        'ФБ': 0
    }

    for card in positive:
        EOB = card.get('EOB', [])
        for x in EOB:
            result[x] = result[x] + 1

    for card in negative:
        EOB = card.get('EOB', [])
        for x in EOB:
            result[x] = result[x] - 1

    positive = {}
    negative = {}

    for key, value in result.items():
        if value < 0:
            negative[key] = value
        if value > 0:
            positive[key] = value

    text = []
    if positive:
        text.append(f'Реальные потребности: {", ".join([f"{value}{key}" for key, value in positive.items()])}')

    if negative:
        text.append(f'Скрытые потребности: {", ".join([f"({value}){key}" for key, value in negative.items()])}')

    text = "\n".join(text)
    text = 'Реальные и скрытые потребности:\n' + text

    image = get_image(result)
    img = image.convert('RGB')
    name = get_random_name('media/results', 'jpg')
    img.save(name)
    return name, text


def sort_f(x):
    keys = {
        "C": 0,
        "T": 1,
        "L": 2,
        "S": 3
    }
    for key, value in keys.items():
        if x[0] == key:
            return int(x.replace(key, '').strip()) + value * 100
    return 0


def formula3(selected_cards):
    if len(selected_cards) != 5:
        return None
    positive = bones_sum(selected_cards[:3])
    negative = bones_sum(selected_cards[3:])

    pos_copy = positive.copy()
    neg_copy = negative.copy()

    for item in positive:
        if item in negative:
            pos_copy.remove(item)

    for item in negative:
        if item in positive:
            neg_copy.remove(item)

    text = []
    if pos_copy:
        pos_copy = sorted(pos_copy, key=lambda x: sort_f(x))
        text.append(f"Реальные: {', '.join(pos_copy)}")
    if neg_copy:
        neg_copy = sorted(neg_copy, key=lambda x: sort_f(x))
        text.append(f"Скрытые: {', '.join(neg_copy)}")
    text = '\n'.join(text)

    img = generate_image(pos_copy, neg_copy)
    img = img.convert('RGB')
    name = get_random_name('media/results', 'jpg')
    img.save(name)
    return name, text


def formula2(selected_cards):
    if len(selected_cards) != 5:
        return None
    positive = selected_cards[:3]
    negative = selected_cards[3:]

    result = 0
    for card in positive:
        power = card.get('power', 0)
        power = int(re.sub(r'\D', '', power))
        result += power

    for card in negative:
        power = card.get('power', 0)
        power = int(re.sub(r'\D', '', power))
        result -= power
    return result


def formula1(selected_cards):
    if len(selected_cards) != 5:
        return None
    positive = selected_cards[:3]
    negative = selected_cards[3:]

    result = []
    for card in positive:
        desc = card.get('desc', '')
        result.append(f'• НЕ {desc}')

    for card in negative:
        desc = card.get('desc', '')
        result.append(f'• {desc}')
    result = '\n'.join(result)
    return result
