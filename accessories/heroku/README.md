### Simple API

The simple API has three endpoints: 
1. to indicate '/status/' (GET)
2. providing '/documentation/' (GET) 
3. to post `mzQC` files to '/validator/' (POST)

The documentation endpoint provides a `dict` with details to each part of the validation (key) as text (value).
The validator endpoint takes a mzQC file (JSON) and responds with an object as described in the documentation endpoint.

### Local Validation & Testing
For local validation and validator development tests, you can start a local validation API like so:
```
python3 -m venv /tmp/vval
source /tmp/vval/bin/activate
pip install -r accessories/heroku/requirements.txt
python accessories/heroku/mzqc_online_validator.py
```
e.g. with `accessories/heroku/local_validator.html`
You can find both files necessary within the repository under [accessories/heroku](https://github.com/MS-Quality-hub/pymzqc/tree/main/accessories/heroku).

### Deploy
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

