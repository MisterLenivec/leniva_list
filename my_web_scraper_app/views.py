import requests
from django.shortcuts import render
from requests.compat import quote_plus
from bs4 import BeautifulSoup
from .models import Search


BASE_CRAIGSLIST_URL = 'https://sfbay.craigslist.org/search/sfc/?query={}'
BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'


def home(request):
    return render(request, 'base.html')


def new_search(request):
    search = request.POST.get('search')
    Search.objects.create(search=search)
    final_url = BASE_CRAIGSLIST_URL.format(quote_plus(search))
    response = requests.get(final_url)
    data = response.text
    soup = BeautifulSoup(data, features='html.parser')

    post_listings = soup.find_all('li', {'class': 'result-row'})

    final_postings = []

    for post in post_listings:
        post_title = post.find(class_='result-title').text

        post_url = post.find('a').get('href')

        if post.find(class_='result-price'):
            post_price = post.find(class_='result-price').text
        else:
            post_price = 'N/A'

        post_image_urls = []

        if post.find(class_='result-image').get('data-ids'):
            post_image_ids = [i[2:] for i in post.find(class_='result-image').get('data-ids').split(',')]
            for i in post_image_ids:
                post_image_urls.append(BASE_IMAGE_URL.format(i))
        else:
            post_image_urls.append('https://craigslist.org/images/peace.jpg')

        final_postings.append((post_title, post_url, post_price, post_image_urls))

    context = {
        'search': search,
        'final_postings': final_postings,
    }

    return render(request, 'my_web_scraper_app/new_search.html', context)
