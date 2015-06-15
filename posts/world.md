title: The World is Calling
date: 2015-06-14
published: true

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

    :::python
    from urlparse import urljoin
    from flask import request
    from werkzeug.contrib.atom import AtomFeed


    def make_external(url):
        return urljoin(request.url_root, url)


    @app.route('/recent.atom')
    def recent_feed():
        feed = AtomFeed('Recent Articles',
                        feed_url=request.url, url=request.url_root)
        articles = Article.query.order_by(Article.pub_date.desc()) \
                          .limit(15).all()
        for article in articles:
            feed.add(article.title, unicode(article.rendered_text),
                     content_type='html',
                     author=article.author.name,
                     url=make_external(article.url),
                     updated=article.last_update,
                     published=article.published)
        return feed.get_response()