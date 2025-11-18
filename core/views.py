from django.shortcuts import render
from django.http import HttpResponse
from store.models import Product
from bestdeal.models import BestDeal 

from store.models import SubBanner
from category.models import Category
def home(request):
    sub_banners = SubBanner.objects.all()
    deals = BestDeal.objects.filter(is_active=True).select_related("product").order_by("display_order")  
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True).order_by('-views', '-cart_added')[:4]
    best_deal_products = Product.objects.filter(
        id__in=deals.values_list("product_id", flat=True),
        is_available=True
    
    )
    context = {
        'sub_banners': sub_banners,
        'best_deal_products': best_deal_products,   # <-- index.html loop
        'best_deals': deals, 
        'products': products,
        'links':categories,
    }
    return render(request, 'index.html', context)
