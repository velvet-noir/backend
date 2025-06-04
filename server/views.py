from django.shortcuts import render
from .data import SERVICES

def service_list(request):
    search_query = request.GET.get('search', '')
    
    filtered_services = SERVICES
    if search_query:
        filtered_services = [
            service for service in SERVICES 
            if search_query.lower() in service['name'].lower() or 
               str(service['price']).lower() == search_query.lower()
        ]
    
    context = {
        'services': filtered_services,
        'search_query': search_query,
    }
    return render(request, 'service_list.html', context)

def service_detail(request, service_id):
    service = next((s for s in SERVICES if s['id'] == service_id), None)
    if not service:
        return render(request, 'services/404.html')
    
    context = {
        'service': service
    }
    return render(request, 'service_detail.html', context)