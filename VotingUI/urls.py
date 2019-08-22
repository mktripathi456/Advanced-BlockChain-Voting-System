from django.urls import path
from VotingUI import views

urlpatterns = [
	path('',views.main_page),
	path('login',views.main_page2),
	path('otp',views.otp_open),
	path('otp_verify',views.otp_verify),
	path('voted',views.candidate_vote),	
	# path('thankyou',views.),
]