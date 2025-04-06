from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from product.models import Product,Category
from .forms import SignUpForm
from allauth.socialaccount.models import SocialAccount
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse

#from django.contrib.auth.models import User # import user from database

# Create your views here.

IMAGES = [
    {"img_name":"home_slide1.png", "title":"Explore This New Collection", "description":"Discover Amazing Cards", "button_text":"Buy Now", "button_link":"/shop/?category=Pokemon"},
    {"img_name":"home_slide2.png", "title":"Apply For The Compettition", "description":"Discover Amazing Cards", "button_text":"Apply Now", "button_link":"#"},
    {"img_name":"home_slide3.jpg", "title":"Discover Cards", "description":"Discover Amazing Cards", "button_text":"Explore Now", "button_link":"/shop/nobita_cry"},
]


def frontpage(request):
    products = Product.objects.filter(is_published=True, is_featured=True)[:8]
    categories = Category.objects.all()

   

    return render(request,'core/frontpage.html',{'products': products, 'categories':categories, "images": IMAGES})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect('/') # redict the front page after succesfully signup the form
    else:
        form = SignUpForm()

    return render(request, 'core/signup.html', {'form': form})

@login_required
def myaccount(request):
    #user = request.user
    #uid = get_social_uid(user, provider='line')
    #print("uid : ",uid)
    order_list = request.user.orders.all().order_by('-created_at')  # Query the model
    paginator = Paginator(order_list, 6)  # 5 objects per page

    page_number = request.GET.get('page')  # Get the page number from request
    page_order = paginator.get_page(page_number)  # Get the page object
    return render(request, 'core/myaccount.html',{'page_order': page_order})

@login_required
def edit_myaccount(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.username = request.POST.get('username')
        user.save()

        return redirect('myaccount')
    return render(request, 'core/edit_myaccount.html')

def shop(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_published=True)
    background_url = None

    active_category = request.GET.get('category','')
    

    if active_category:
        products = products.filter(category__slug=active_category)
        category = get_object_or_404(Category, slug=active_category)
        
        if category.background:    
            background_url = category.background.url    
        else:
            background_url = None
        
    query = request.GET.get('query', '')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    
    context = {
        'categories': categories,
        'products': products,
        'active_category': active_category,
        'background_url': background_url
        

    }
    return render(request,'core/shop.html',context)

## Test ##

#def forcelogin(request):
#    user = User.objects.get(pk='3')
#    login(request, user)
#    return render(request, 'core/frontpage.html')


def get_social_uid(user, provider=None):
    """
    Retrieve the social account UID for a given user and provider.
    :param user: The Django user instance.
    :param provider: The social provider (e.g., 'google', 'facebook').
                     If None, retrieves the UID for the first linked social account.
    :return: The UID (unique identifier) of the social account or None.
    """
    try:
        if provider:
            social_account = SocialAccount.objects.get(user=user, provider=provider)
        else:
            social_account = SocialAccount.objects.filter(user=user).first()
        return social_account.uid if social_account else None
    except SocialAccount.DoesNotExist:
        return None