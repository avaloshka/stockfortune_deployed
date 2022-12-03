from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	path('', views.home, name='home'),
	path('introduction', views.introduction, name='introduction'),
	path('members', views.members, name='members'),
	path('join', views.join, name='join'),
	path('strategy', views.strategy, name='strategy'),
	path('magic', views.magic, name='magic'),
	path('protecting_your_trade', views.protecting_your_trade, name='protecting_your_trade'),
	path('charts', views.charts, name='charts'),
	path('your_stock', views.your_stock, name='your_stock'),
	path('buy_half_price', views.buy_half_price, name='buy_half_price'),
	path('conclusion', views.conclusion, name='conclusion'),
] 

# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)