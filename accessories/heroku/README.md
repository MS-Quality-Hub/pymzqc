## Simple mzqc-validator API

The simple API has three endpoints: 
1. to indicate '/status/' (GET)
2. providing '/documentation/' (GET) 
3. to post `mzQC` files to '/validator/' (POST)

The documentation endpoint provides a `dict` with details to each part of the validation (key) as text (value).
The validator endpoint takes a mzQC file (JSON) and responds with an object as described in the documentation endpoint.
### Build
From the root of the pymzqc source folder (i.e. build context `pymzqc/`) build the `accessories/heroku/Dockerfile`, e.g. with podman:
```
podman build -t mzqc-validator -f accessories/heroku/Dockerfile .
```
(If you are testing a release without pypi package uncomment the respective lines in the Dockerfile to override the pymzqc version used.)

### Deployment
To test the deployment run the mzqc-validator flask app in gunicorn from the container (as described in `wsgi.py`). 
```
podman run -p 5000:5000 -ti localhost/mzqc-validator python3 -m gunicorn wsgi:app -b 0.0.0.0:5000 --chdir mzqc-validator/
```
For local tests calling the flask app directly (i.e. as single thread app) is fine too: `python accessories/heroku/mzqc_online_validator.py`; note that the ports might differ, depending on the flask defaults. 
The mzQC gitHub-pages integration and `local_validator.html` expect the API to run on port 5000.
Calling the mzqc_online_validator directly in gunicorn is fine too (`podman run -p 8123:8123 -ti localhost/mzqc-validator python3 -m gunicorn mzqc_online_validator:app -b 0.0.0.0:8123 --chdir mzqc-validator/`), the `wsgi.py` indirection is a legacy effect from heroku's Procfile use and their example app.

#### Legacy Heroku Deployment
Or you can deploy your own heroku dyno like so:
```
cd /tmp/
curl https://cli-assets.heroku.com/install-ubuntu.sh | sh
heroku login
heroku git:clone -a mzqc-validator 
cd mzqc-validator
rsync -aP --delete /home/walzer/psi/pymzqc/acessories/heroku  /tmp/mzqc-validator
git push heroku master
```

### Local Testing
First use `dev-test-validation.py` as testbed for new changes.

Then, you can build and deploy the container as described above and access the API e.g. with `accessories/heroku/local_validator.html`
You can find both files necessary within the repository under [accessories/heroku](https://github.com/MS-Quality-hub/pymzqc/tree/main/accessories/heroku).
