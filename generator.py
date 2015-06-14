import os
import sys
import collections
from datetime import datetime

from flask import Flask, render_template, url_for, abort, request
from flask.ext.frozen import Freezer
from werkzeug import cached_property
from werkzeug.contrib.atom import AtomFeed
import markdown
import yaml

POSTS_FILE_EXTENSION = '.md'

class SortedDict(collections.MutableMapping):
    def __init__(self, items=None, key=None, reverse=False):
        self._items = {}
        self._keys = []
        if key:
            self._key_fn = lambda k: key(self._items[k])
        else:
            self._key_fn = lambda k: self._items[k]
        self._reverse = reverse

        if items is not None:
            self.update(items)

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key, value):
        self._items[key] = value
        if key not in self._keys:
            self._keys.append(key)
            self._keys.sort(key=self._key_fn, reverse=self._reverse)

    def __delitem__(self, key):
        self._items.pop(key)
        self._keys.remove(key)

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        for key in self._keys:
            yield key

    def __repr__(self):
        sorted_dict = '{'
        for key in self._keys:
            sorted_dict += '%s: %s, ' % (key, self._items[key])
        sorted_dict = sorted_dict[:-2] + '}'
        return '%s(%s)' % (self.__class__.__name__, sorted_dict)

class Blog(object):
    def __init__(self, app, root_dir='', file_ext=POSTS_FILE_EXTENSION):
        self.root_dir = root_dir
        self.file_ext = file_ext
        self._app = app
        self._cache = SortedDict(key=lambda p: p.date, reverse=True)
        self._initialize_cache()

    @property
    def posts(self):
        return self._cache.values()

    def get_post_or_404(self, path):
        """Returns the Post object for the given path or raises a NotFound exception
        """
        try:
            return self._cache[path]
        except KeyError:
            abort(404)

    def _initialize_cache(self):
        """Walks the root directory and adds all posts to the cache
        """
        for (root, dirpaths, filepaths) in os.walk(self.root_dir):
            for filepath in filepaths:
                filename, ext = os.path.splitext(filepath)
                if ext == self.file_ext:
                    path  = os.path.join(root, filepath).replace(self.root_dir, '')
                    post = Post(path, root_dir=self.root_dir)
                    self._cache[post.urlpath] = post

class Post(object):
    def __init__(self, path, root_dir=''):
        self.urlpath = os.path.splitext(path.strip('/'))[0]
        self.filepath = os.path.join(root_dir, path.strip('/'))
        self._initialize_metadata()

    @cached_property
    def html(self):
        with open(self.filepath, 'r') as fin:
            content = fin.read().split('\n\n', 1)[1].strip()
        return markdown.markdown(content)

    def url(self, _external=False):
        return url_for('post', path=self.urlpath, _external=_external)


    def _initialize_metadata(self):
        with open(self.filepath, 'r') as fin:
            content = ''
            for line in fin:
                if not line.strip():
                    break
                content += line
        self.__dict__.update(yaml.load(content))

app = Flask(__name__)
blog = Blog(app, root_dir='posts')
freezer = Freezer(app)

@app.template_filter('date')
def format_date(value, format='%B %d, %Y'):
    return value.strftime(format)

@app.route('/')
def index():
    return render_template('index.html', posts=blog.posts)

@app.route('/blog/<path:path>/')
def post(path):
    post = blog.get_post_or_404(path)
    return render_template('post.html', post=post)

# http://flask.pocoo.org/snippets/10/
@app.route('/feed.atom')
def recent_feed():
    feed = AtomFeed('Recent Articles',
                    feed_url=request.url,
                    url=request.url_root)
    posts = blog.posts[:10]
    title = lambda p: '%s: %s' % (p.title, p.subtitle) if hasattr(p, 'subtitle') else p.title
    for post in posts:
        post_date = datetime.combine(post.date, datetime.min.time())    # https://github.com/mitsuhiko/werkzeug/issues/695
        feed.add(title(post),
                 unicode(post.html),
                 content_type='html',
                 author='Parth P Panchal',
                 url=post.url(_external=True),
                 updated=post_date,
                 published=post_date)
    return feed.get_response()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'build':
        freezer.freeze()
    else:
        post_files = [post.filepath for post in blog.posts]
        app.run(port=8000, debug=True, extra_files=post_files)