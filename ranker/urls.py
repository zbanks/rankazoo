from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rankazoo.views.home', name='home'),
    url(r'^$', 'rankazoo.ranker.views.index', name='index'),
#url(r'^addaxis$', 'rankazoo.ranker.views.addaxis', name='addaxis'),
    url(r'^axis(?:/(?P<axis_slug>[\w-]+))?$', 'rankazoo.ranker.views.axis', name='axis'),
    url(r'^item(?:/(?P<item_slug>[\w-]+))?$', 'rankazoo.ranker.views.item', name='item'),
    url(r'^rank/(?P<axis_slug>[\w-]+)/(?P<item_slug>[\w-]+)$', 'rankazoo.ranker.views.rank', name='rank'),

    url(r'^chart/(?P<axis_x_slug>[\w-]+)/(?P<axis_y_slug>[\w-]+)$', 'rankazoo.ranker.views.chart', name='chart'),
)
