# Notes

To use this docker image, you need to have a look at the follogin things:

1. Adding your host to `Allowed Hosts` in `conf/settings.py` (line 32)

2. Remove
   ```
   ports:
     8000:8000
   ```
   in `docker-compose.yml` to prevent access from outside, or if you're using a reverse proxy.

**IMPORTANT:** Don't use in production. For productional use (deployment), you should read the missing features and the helfertool readme.

# Missing

* MySQL or Postgresql instead of Sqlite
* Mails / SMTP Server#
* LaTex