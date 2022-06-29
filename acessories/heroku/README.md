

# deploy
```
cd /tmp/
curl https://cli-assets.heroku.com/install-ubuntu.sh | sh
heroku login
heroku git:clone -a mzqc-validator 
cd mzqc-validator
rsync -aP --delete /home/walzer/psi/pymzqc/acessories/heroku  /tmp/mzqc-validator
git push heroku master
```
# test
```
python3 -m venv /tmp/vval
source /tmp/vval/bin/activate
pip install -r mzqc-validator/requirements.txt 
python mzqc-validator/mzqc_heroku_validator.py
```
e.g. with `file:///tmp/doc/gh-page/pages/_validator_alone.html`