from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Cart, CartItem
from store.models import Product , Variation
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Coupon.forms import ApplyCouponForm
from Coupon .models import Coupon
from order .models import Order, Payment, OrderProduct
import datetime
from django.utils import timezone
# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart



# Helper function to handle adding items to cart gpt start
def _handle_cart_item(cart_item, product_variation):
    if product_variation in cart_item['existing_variation_list']:
        index = cart_item['existing_variation_list'].index(product_variation)
        item_id = cart_item['id'][index]
        item = CartItem.objects.get(product=cart_item['product'], id=item_id)
        item.quantity += 1
        item.save()
    else:
        item = CartItem.objects.create(
            product=cart_item['product'], 
            quantity=1, 
            user=cart_item['user'], 
            cart=cart_item.get('cart', None)
        )
        if product_variation:
            item.variations.clear()
            item.variations.add(*product_variation)
        item.save()
# Helper function to handle adding items to cart gpt end

    # add to cart
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)#get the product
    
    product_variation = [] #gpt teke niye ami akn aai line ta diyeci
    # if user is not authenticated
    if current_user.is_authenticated:
        # product_variation = [] ai line ta hide korci karon gpt akn a ai code dai nai opore diyece
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
        # color = request.POST['color'] #<select name="color"> ja takbe akn tai name dibo['color] 
        # size = request.POST['size']
        # print(color, size)

        #msg
        messages.success(request, "product added successfully")
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product , user=current_user)
            # existing variation -> database
            # carrent variation -> product_variation
            # item_id -> database
            existing_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)
            # print(existing_variation_list)

            if product_variation in existing_variation_list:
                index = existing_variation_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            if len (product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')

    # if user is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
            # color = request.POST['color'] #<select name="color"> ja takbe akn tai name dibo['color] 
            # size = request.POST['size']
            # print(color, size)

        
        try:
            cart = Cart.objects.get(cart_id= _cart_id(request)) #get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product , cart=cart)
            existing_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)
            print(existing_variation_list)

            if product_variation in existing_variation_list:
                index = existing_variation_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len (product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')

#remove from cart
def remove_from_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

# remove or delete cart

def remove(request,product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    #cupon method start
    # code = request.POST.get('coupon_code')
    # carts = CartItem.objects.filter(user=request.user)  # Adjust this to your cart logic
    # now = timezone.now()
    # try:
    #     coupon = get_object_or_404(Coupon, code=code, active=True, valid_from__lte=now, valid_to__gte=now)
    #     # Check if the coupon applies to any product in the cart
    #     applicable_items = cart_items.filter(product__in=coupon.applicable_products.all())
        
    #     if applicable_items.exists():
            
    #         # Apply the coupon to the eligible items in the cart
    #        for item_product in applicable_items:
    #         discount_amount = item_product.product.price * (coupon.discount / 100)
    #         item_product.discounted_price = item.product.price - discount_amount
    #         item_product.save()

    #         messages.success(request, f'Coupon "{coupon.code}" applied successfully!')
    #     else:
    #         messages.error(request, 'Coupon is not valid for any items in your cart.')

    # except Coupon.DoesNotExist:
    #     messages.error(request, 'Invalid or expired coupon code.')

    # return redirect('cart')  # Redirect to your cart page
    # #coupon method end
    try:
        vat = 0
        total_price = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
           
        vat = (1 * total)/100
        total_price = total + vat
        # delevary += 60

        # Handle coupon application start
        if request.method == 'POST':
            code = request.POST.get('coupon_code')
            now = timezone.now()
            try:
                coupon = Coupon.objects.get(code=code, active=True, valid_from__lte=now, valid_to__gte=now)
                applicable_items = cart_items.filter(product__in=coupon.applicable_products.all())
                if applicable_items.exists():
                    for item_product in applicable_items:
                        discount_amount = item_product.product.price * (coupon.discount / 100)
                        item_product.discounted_price = item_product.product.price - discount_amount
                        item_product.save()
                    messages.success(request, f'Coupon "{coupon.code}" applied successfully!')
                messages.success(request, f'Coupon "{coupon.code}" applied successfully!')

            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid or expired coupon code.')

        # Handle coupon application end

    except ObjectDoesNotExist:
        pass

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'vat': vat,
        'total_price' : total_price,
        # 'delevary' : delevary,
    }
    return render(request, 'cart/cart.html', context)

#checkout page design:
@login_required(login_url='login') #ai line ta use korar karon amra jodi site a login kora nah take tahole amra cart product gula jodi checkout korar time a amake login korte bola hobe 
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        vat = 0
        total_price = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
           
        vat = (1 * total)/100
        total_price = total + vat
        # delevary += 60
    except ObjectDoesNotExist:
        pass

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'vat': vat,
        'total_price' : total_price,
        # 'delevary' : delevary,
    }
    return render(request, 'cart/checkout.html',context)