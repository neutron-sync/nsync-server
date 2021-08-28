# Neutron Sync Server

### *Encrypted Dot File sync service*

This is the web service portion of Neutron Sync. It is a Django app and can be deployed just like any other Django web service.

## Setup

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
```
