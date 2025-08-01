from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Product, Variation
from django.db.models import Q
from category.models import Category
from carts.views import _cart_id
from carts.models import CartItem, Cart
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 2)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 5)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, subcategory_slug, subsubcategory_slug, product_slug):
    
    try:
        # single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        single_product = get_object_or_404(Product,category__slug=category_slug,subcategory__slug=subcategory_slug,subsubcategory__slug=subsubcategory_slug,slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        
    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    }

    return render(request, 'store/product_detail.html', context)

#search diye kojar jnno use korteci
def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)