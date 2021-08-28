# Neutron Sync Server

### *Encrypted Dot File sync service*

This is the web service portion of Neutron Sync. It is a Django app and can be deployed just like any other Django web service.

## Setup Service

**Requires:**

- Python 3
- [PDM](https://pdm.fming.dev/)
- PostgreSQL Database

```
git clone git@github.com:neutron-sync/nsync-server.git

cd nsync-server
pdm install

# Generate a key at: https://djecrety.ir/
echo SECRET_KEY=<YOUR_SECRET_KEY> > .env

# Database Setup
createdb nsync
pdm run manage migrate

pdm run manage createsuperuser

# ENV setup
echo ALLOWED_HOSTS=<YOUR-DOMAIN.COM> >> .env
echo AWS_ACCESS_KEY_ID=<YOUR KEY> >> .env
echo AWS_S3_REGION_NAME=<YOUR REGION> >> .env
echo AWS_SECRET_ACCESS_KEY=<YOUR SECRET> >> .env
echo AWS_STORAGE_BUCKET_NAME=<YOUR BUCKET> >> .env
```

Additional ENV Vars:

- `DATABASE_URL`: Override default database URL

## Running The Service

For testing: `pdm run manage runserver`

In production: `gunicorn nsync_server.nsync.wsgi:application`

## Configuring the CLI Client

Adjust your config file (`~/.config/nsync/config.json`)

`"server_url": "https://your-domain.com",`

## Further Setup

It is recommended to run this service behind an HTTP load balancer like Nginx. The files required to deploy this service with the Build Pack standard are included. Services like [Heroku](https://www.heroku.com/) and [Digital Ocean](https://www.digitalocean.com/) support the Build Pack standard for deployment.
