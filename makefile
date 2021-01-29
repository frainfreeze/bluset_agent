APP_NAME=bluset_agent

setup:
	@echo "Installing packages..."
	sudo apt install python3 python3-pip goaccess geoip-database
	sudo pip3 install flask
	@echo "Seting up system services..."
	sudo cp deployment/$(APP_NAME).service /etc/systemd/system/$(APP_NAME).service
	sudo systemctl start $(APP_NAME).service
	sudo systemctl enable $(APP_NAME).service
	sudo systemctl daemon-reload
	@echo "Seting up reverse proxy..."
	sudo cp deployment/$(APP_NAME).conf /etc/nginx/sites-enabled/default
	sudo service nginx restart

run:
	(export FLASK_APP=main.py && flask run)
