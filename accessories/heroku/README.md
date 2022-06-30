### simple API

The simple API has three endpoints: 
1. indicating '/status/' (GET)
2. providing '/documentation/' (GET) 
3. to post `mzQC` files to '/validator/' (POST)

The documentation provides a `dict` with details to each part of the validation (key) as text (value).

### test & local validation
```
python3 -m venv /tmp/vval
source /tmp/vval/bin/activate
pip install -r accessories/heroku/requirements.txt
python accessories/heroku/mzqc_heroku_validator.py
```
e.g. with `accessories/heroku/local_validator.html`

### deploy
```
cd /tmp/
curl https://cli-assets.heroku.com/install-ubuntu.sh | sh
heroku login
heroku git:clone -a mzqc-validator 
cd mzqc-validator
rsync -aP --delete /home/walzer/psi/pymzqc/acessories/heroku  /tmp/mzqc-validator
git push heroku master
```

