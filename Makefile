export LOG_LEVEL='DEBUG'
export FACEBOOK_APP_ID=123
export FACEBOOK_SECRET=12345

smoke :
	@printenv | grep FACEBOOK
	python facebookgeoapp.py
	echo done

lint :
	pylint facebookgeoapp.py