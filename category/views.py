from django.shortcuts import render
from .models import Category
from store.models import Product

def home(request):
    categories = Category.objects.all()
    
    context = {
        'categories': categories,
    }
    return render(request, 'index.html', context)