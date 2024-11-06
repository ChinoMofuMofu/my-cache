from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.cache import cache
import json

def test(request):
    print(request.path.strip('/'))
    return HttpResponse("HelloWorld\n")

def update(data):
    for k, v in data.items():
        cache.set(k, v, timeout = None)

def get_value(key):
    if cache.has_key(key):
        status = 200
        return status, cache.get(key)
    else:
        status = 404
        return status, None

def delete(key):
    if cache.has_key(key):
        cache.delete(key)
        return 1
    else:
        return 0

def request_process(request):
    print("request process")
    method = request.method
    if method == 'POST':
        try:
            data = json.loads(request.body)
            update(data)
            return HttpResponse(status = 200)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    elif method == 'GET':
        key = request.path.strip('/')
        status, res = get_value(key)
        print(res)
        if status == 200:
            return JsonResponse({key : res}, status=200, json_dumps_params={'ensure_ascii': False})
        else:
            return HttpResponse(status=404)
    elif  method == 'DELETE':
        key = request.path.strip('/')
        res = delete(key)
        return HttpResponse(res, status = 200)
