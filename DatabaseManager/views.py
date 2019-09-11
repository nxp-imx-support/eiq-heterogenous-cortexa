__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

from Recognition.models import LogsDatabase, ImageDatabase
from django.http import JsonResponse
from Recognition.models import ImageDatabase

# Create your views here.
def return_logs(request):
    try:
        logs = LogsDatabase.objects.all()
    except LogsDatabase.DoesNotExist:
        logs = None

    response = dict()

    if logs:
        for log in logs:
            id = log.id
            name = log.name
            face = log.face.url
            timestamp = log.timestamp
            known = log.known

            response[id] = dict()
            response[id]['name'] = name
            response[id]['face'] = face
            response[id]['timestamp'] = timestamp
            response[id]['known'] = known
    else:
        response['response'] = "Logs non existent"

    return JsonResponse(response)


def get_active_users(request):
    try:
        users = ImageDatabase.objects.all()
    except ImageDatabase.DoesNotExist:
        users = None

    response = dict()
    if users:
        for user in users:
            response[user.id] = dict()
            response[user.id]['name'] = user.name
            try:
                response[user.id]['picture'] = user.face.url
            except ValueError as e:
                # might not have the picture set at this point
                response[user.id]['picture'] = ""
                pass

    else:
        response['response'] = "No active users"

    return JsonResponse(response)


def return_user_info_id(request, user_id):
    try:
        entry = ImageDatabase.objects.get(id=user_id)
    except ImageDatabase.DoesNotExist:
        entry = None

    response = dict()

    if entry:
        id = entry.id
        name = entry.name
        # might not have the picture set at this point
        try:
            face = entry.face.url
        except ValueError as e:
            # might not have the picture set at this point
            face = ""
            pass

        response[id] = dict()
        response[id]['name'] = name
        response[id]['face'] = face
    else:
        response['response'] = "User with given id non existent"

    return JsonResponse(response)

def return_user_info_name(request, user_name):
    try:
        entries = ImageDatabase.objects.filter(name=user_name)
    except ImageDatabase.DoesNotExist:
        entries = None

    response = dict()

    if entries:
        for entry in entries:
            id = entry.id
            name = entry.name
            face = entry.face.url

            response[name + str(id)] = dict()
            response[name + str(id)]['name'] = name
            response[name + str(id)]['face'] = face
    else:
        response['response'] = "User with given name non existent"

    return JsonResponse(response)
