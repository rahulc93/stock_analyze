from django.conf.urls import url
from stock import views

urlpatterns = [
    #url(r'^$', views.index, name = 'index')

    
    url(r'^stock/$', views.stock, name = 'stock'),
    
    url(r'^enter$', views.stock_enter, name = 'stock_enter'),
    
    url(r'^clear$', views.stock_clearall, name = 'stock_clearall'),

	url(r'^goc/(?P<comp_code>[0-9]+)/(?P<date>[0-9]+)/$', views.goc, name = 'goc'),
	
	url(r'^goc_range/(?P<comp_code>[0-9]+)/(?P<start_date>[0-9]+)/(?P<end_date>[0-9]+)/$', views.goc_range, name = 'goc_range'),

    ]
