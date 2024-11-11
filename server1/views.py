from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.cache import cache
import json
import requests
import hashlib

server_ip = '47.109.100.46'
#server_ip = '127.0.0.1'

def test(request):
    print(request.path.strip('/'))
    return HttpResponse("HelloWorld\n")

def calculate_server_num(x):
    hash_obj = hashlib.md5(x.encode())
    v = int(hash_obj.hexdigest(), 16)
    return v % 3

def update(data):
    for k, v in data.items():
        sv = calculate_server_num(k)
        if sv == 0:
            cache.set(k, v, timeout = None)
        elif sv == 1:
            url = f'''http://{server_ip}:9528'''
            requests.post(url, json = {k : v}, verify = False)
        elif sv == 2:
            url = f'''http://{server_ip}:9529'''
            data = {k : v}
            requests.post(url, json = {k : v}, verify = False)

def get_value(key):
    sv = calculate_server_num(key)
    if sv == 0:
        if cache.has_key(key):
            status = 200
            return status, cache.get(key)
        else:
            status = 404
            return status, None
    else:
        if sv == 1:
            url = f'''http://{server_ip}:9528/{key}'''
            response = requests.get(url)
        elif sv == 2:
            url = f'''http://{server_ip}:9529/{key}'''
            response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return 200, data[key]
        else:
            return 404, None

def delete(key):
    sv = calculate_server_num(key)
    if sv == 0:
        if cache.has_key(key):
            cache.delete(key)
            return 1
        else:
            return 0;
    else:
        if sv == 1:
            url = f'''http://{server_ip}:9528/{key}'''
            response = requests.delete(url)
        elif sv == 2:
            url = f'''http://{server_ip}:9529/{key}'''
            response = requests.delete(url)

        return response.text

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
