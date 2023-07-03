from django.http import HttpResponse
from django.shortcuts import render
from rango.models import Category, Page
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from rango.forms import CategoryForm
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from .models import Category, Page
from django.shortcuts import render
from django.conf import settings
from rango.keys import BING_SEARCH_API_KEY
import requests


@login_required
def index(request):
    request.session.set_test_cookie()
    # Gets the top 5 categories and pages and saved it to context_dict
    page_list = Page.objects.order_by('-views')[:5]
    category_list = Category.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'page_list': page_list}

    response = render(request,'rango/index.html', context_dict)
    return response


def about(request):
    # Capture visit counts for about html
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0
    context = {
        'about': 'This is Rango about page.',
        'visits': count,
    }
    return render(request, 'rango/about.html', context)


def category(request, category_name_url):

    # replacing spaces with _ to avoid errors for url.
    category_name = category_name_url.replace('_', ' ')
    context_dict = {'category_name': category_name}

    try:
        # Saving the Category being accessed and extract all related pages
        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
        # Increment the views value of the Category
        category.increment_views()
        category.save()

    except Category.DoesNotExist:
        pass

    return render(request, 'rango/category.html', context_dict)


@login_required 
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    return render(request, 'rango/add_category.html', {'form': form})


@login_required 
def add_page(request, category_name_url):
    # Retrieve the category object based on the category_name_url parameter
    category = get_object_or_404(Category, name=category_name_url)
    
    if request.method == 'POST':
        # Retrieve the form data submitted by the user
        title = request.POST.get('title')
        url = request.POST.get('url')
        views = int(request.POST.get('views', 0))

        # Create a new page object
        page = Page(title=title, url=url, views=views)
        # Associate the page with the category
        page.category = category
        # Save the page object to the database
        page.save()
        # Perform any additional logic or redirection as needed
        # ...

    # Render the template for adding a page
    return render(request, 'rango/add_page.html', {'category': category})


def register(request):
    if request.session.test_cookie_worked():
        print(">>>> TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print(user_form.errors, profile_form.errors)

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request,
            'rango/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered} )


def user_login(request):

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
                # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
                # because the request.POST.get('<variable>') returns None, if the value does not exist,
                # while the request.POST['<variable>'] will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'rango/login.html', {})
    

def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")


def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/rango/')


def search_view(request):
    query = request.GET.get('query')
    api_key = BING_SEARCH_API_KEY
    endpoint = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {"q": query, "count": 10}  # Customize parameters as needed

    response = requests.get(endpoint, headers=headers, params=params)
    results = response.json().get('webPages', {}).get('value', [])

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'rango/search_results.html', context)

def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)

@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes =  likes
            cat.save()

    return HttpResponse(likes)


def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    return cat_list


def suggest_category(request):
    cat_list = []
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']

    cat_list = get_category_list(8, starts_with)
    
    return render(request, 'rango/cats.html', {'cat_list': cat_list})


@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)

            pages = Page.objects.filter(category=category).order_by('-views')

            # Adds our results list to the template context under name pages.
            context_dict['pages'] = pages

    return render(request, 'rango/page_list.html', context_dict)