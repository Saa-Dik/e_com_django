from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Product, Variation
from django.db.models import Q
from category.models import Category 
from carts.views import _cart_id
from carts.models import CartItem, Cart
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from order.models import Order, OrderProduct
from reviews.models import Review
from django.db.models import Q, Min, Max 
from bestdeal.views import best_deals
from flashsale.views import flash_sale
from django.shortcuts import render, get_object_or_404
# Create your views here.
# def store(request, category_slug=None):
#     categories = None
#     products = None # 11-13-2025
#     if category_slug != None:
#         categories = get_object_or_404(Category, slug=category_slug)
#         products = Product.objects.filter(category=categories, is_available=True) # 11-13-2025
#         paginator = Paginator(products, 2)
#         page = request.GET.get('page')
#         paged_products = paginator.get_page(page)
#         product_count = products.count()
#     else:
#         products = Product.objects.all().filter(is_available=True).order_by('id')
#         paginator = Paginator(products, 5)
#         page = request.GET.get('page')
#         paged_products = paginator.get_page(page)
#         product_count = products.count()
#     context = {
#         'products': paged_products,
#         'product_count': product_count,
#     }
#     return render(request, 'store/store.html', context)
def store(request, category_slug=None):
    category = None
    products = None

    # ============================
    # CATEGORY FILTER
    # ============================
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
    else:
        products = Product.objects.filter(is_available=True)

    # ============================
    # SIZE FILTER
    # ============================
    selected_size = request.GET.get('size')
    if selected_size:
        products = products.filter(variation__variation_category='size',variation__variation_value__iexact=selected_size)

    # Collect all sizes available
    available_sizes = (Variation.objects.filter(variation_category='size').values_list('variation_value', flat=True).distinct())

    # ============================
    # COLOR FILTER
    # ============================
    selected_color = request.GET.get('color')
    if selected_color:
        products = products.filter(variation__variation_category='color',variation__variation_value__iexact=selected_color)

    # Collect all colors available
    available_colors = (Variation.objects.filter(variation_category='color').values_list('variation_value', flat=True).distinct())

    # ============================
    # PRICE FILTER
    # ============================
    price_min = Product.objects.all().order_by('price').first().price if Product.objects.exists() else 0
    price_max = Product.objects.all().order_by('-price').first().price if Product.objects.exists() else 1000

    selected_min_price = request.GET.get('min_price')
    selected_max_price = request.GET.get('max_price')

    if selected_min_price:
        products = products.filter(price__gte=selected_min_price)
    if selected_max_price:
        products = products.filter(price__lte=selected_max_price)

    # ============================
    # PAGINATION
    # ============================
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,

        # Filters
        'available_sizes': available_sizes,
        'available_colors': available_colors,
        'price_min': price_min,
        'price_max': price_max,

        'selected_size': selected_size,
        'selected_color': selected_color,
        'selected_min_price': selected_min_price,
        'selected_max_price': selected_max_price,
    }
    return render(request, 'store/store.html', context)

#search diye kojar jnno use korteci
def search(request):

    products = Product.objects.none()   # default empty
    product_count = 0                   # default count
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


# def product_detail(request, category_slug, product_slug):
#     try:
#         single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
#         in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
#     except Exception as e:
#         raise e

#     if request.user.is_authenticated:
#         try:
#             order_product = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
#         except OrderProduct.DoesNotExist:
#             order_product = None
#     else:
#         order_product = None

#
#     reviews = Review.objects.filter(product_id=single_product.id, status=True).order_by('-created_at')

#     context = {
#         'single_product': single_product,
#         'in_cart': in_cart,
#         'orderproduct': order_product,
#         'reviews': reviews,   # 
#     }
#     return render(request, 'store/product_detail.html', context)


def product_detail(request, category_slug, product_slug):

    single_product = get_object_or_404(
        Product,
        category__slug=category_slug,
        slug=product_slug,
    )


    in_cart = CartItem.objects.filter(
        cart__cart_id=_cart_id(request),
        product=single_product
    ).exists()

    
    if request.user.is_authenticated:
        order_product = OrderProduct.objects.filter(
            user=request.user,
            product_id=single_product.id
        ).exists()
    else:
        order_product = None


    reviews = Review.objects.filter(
        product=single_product,
        status=True
    ).order_by('-created_at')

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': order_product,
        'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context)

def hot_deals(request):
    products = Product.objects.filter(is_available=True).order_by('-created_date')[:3]
    context = {
        'products': products,
    }
    return render(request, 'store/hot_deals.html', context)