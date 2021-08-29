# Neutron Sync Server

### *Encrypted Dot File sync service*

This is the web service portion of Neutron Sync. It is a Django app and can be deployed just like any other typical Django web service.

The server provides the following functions that are used by the CLI client:

- User management
- GraphQL API
- Remote file storage

## Setup Service

**Requires:**

- Python 3
- [PDM](https://pdm.fming.dev/)
- PostgreSQL Database
- S3 compatible storage (optional)

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

# Storage Bucket Setup (optional)
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

## Configure the CLI Client

Adjust your config file (`~/.config/nsync/config.json`)

`"server_url": "https://your-domain.com",`

## Administration

The open source version of the Neutron Sync server does not come with a custom UI. However, the Django admin located at `/admin/` should provide you with enough functionality for you and your users to maintain and manage their accounts.

## Further Setup

It is recommended to run this service behind an HTTP load balancer like Nginx. The files required to deploy this service with the [Build Pack](https://buildpacks.io/) standard are included. Services like [Heroku](https://www.heroku.com/) and [Digital Ocean](https://www.digitalocean.com/) support the Build Pack standard for deployment.
