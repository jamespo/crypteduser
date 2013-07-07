crypteduser

Tiny authentication server written in python & flask.

Usage
-----

Edit the configuration file

Add a user
* curl -i -d username=jamesp -d password=WombleW1m http://127.0.0.1:5000/adduser/

Check password
* curl -i -d username=jamesp -d password=WombleW1m http://127.0.0.1:5000/verifyuser/

Update password
* curl -i -d username=jamesp -d password=WombleW1m http://127.0.0.1:5000/updatepass/

Notes
-----

If you run this over the network (ie - not over localhost), put an a SSL-terminating proxy in front.
Do not send the usernames & passwords over in plain text. Do not run in debug mode in production.
