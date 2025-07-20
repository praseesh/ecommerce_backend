from django.shortcuts import HttpResponse

from django.core.cache import cache


def cache_set_get_method(request):
    cache.set('orange', '100', timeout=60*1)
    cache.set('mango', 50, timeout=60)
    value = cache.get('orange') 
    mangos = cache.get('mango') 
    print(f'Apple: {value}')
    print(f'Mango: {mangos}')

    return HttpResponse(f'apple value: {value}\nmango value: {mangos}')