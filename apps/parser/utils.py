import os
import slumber
import requests

from django.conf import settings
from django.template.loader import render_to_string


def get_slumber_api(root, access_token):
    session = requests.session(
        params={'access_token': access_token}
    )
    return slumber.API(root, session=session)


def parse_blog_posts(process, max_pages, page_token=None, page_size=20):
    blog = process.blog
    api = get_slumber_api(
        settings.BLOGGER_API_ROOT,
        blog.source.access_token
    )
    data = api.blogs(blog.identificator).posts().get(
        pageToken=page_token, maxResults=page_size,
    )
    nextPageToken = data.get('nextPageToken')
    posts = data.get('items', [])
    if not posts:
        return
    convert_blog_posts(process, posts)

    max_pages -= 1
    if not max_pages <= 0 and nextPageToken is not None:
        get_blog_posts(process, max_pages, nextPageToken, page_size)


def get_post_slug(domain, full_url):
    slug = full_url.replace('http://{0}'.format(domain), '')
    slug = slug.replace('.html', '')
    return slug[1:]


def convert_blog_posts(process, posts):
    content_root = os.path.join(process.path, 'content')
    os.makedirs(content_root)
    domain = process.blog.domain
    for post in posts:
        slug = get_post_slug(domain, post.get('url'))
        file_name = slug.replace('/', '-')
        file_path = os.path.join(content_root, file_name)
        file_path = '{0}.md'.format(file_path)
        convert_blog_post(post, slug, file_path)


def convert_blog_post(post, slug, file_path):
    with open(file_path, 'w') as f:
        f.write(render_to_string('parser/post.md', {
            'post': post, 'slug': slug
        }))
