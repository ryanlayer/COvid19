## Local Setup


- Get mapbox public token, put it in `.mapbox_token`
- Run Snakefile commands to generate weekend score, slip score, and trend csv - verify their location in `location_data` directory
- Generate weekend score, slip score, and trend csv and put them in the 'dash' directory
- Verify pathname accuracy in `cities.tsv'
- Start the app

```
$ python local_dash.py
```
Goto the local page at `http://127.0.0.1:8050/`

- The default city is defined in `local_dash.py` as Boulder. To change city of interest, input the name directly into the url as such:

```
$ 'http://127.0.0.1:8050/boulder' or 'http://127.0.0.1:8050/denver'
```

## Dash Enterprise Setup

- Get mapbox public token, put it in `.mapbox_token`
- Run Snakefile commands to generate weekend score, slip score, and trend csv - verify their location in `location_data` directory
- Generate weekend score, slip score, and trend csv and put them in the 'dash' directory
- Verify pathname accuracy in `cities.tsv'
- Input the name of your Dash Enterprise App into the `app_url_name` variable in `app.py`
- Push code to Dash Enterprise Repo
### The Dash Enterprise code is in `app.py` not `local_dash.py`. 
```
$ git init
```
```
$ git add .
```
```
$ git -m "commit message"
```
```
$  git remote add plotly https://dash-boulder.plotly.host/GIT/YOUR_APP_NAME
```
```
$ git push plotly master
```
-Open the Dash Enterprise web service and open your app - all log and error messages with be accessible here.
-The The default city is defined in `app.py` as Boulder. To change city of interest, input the name directly into the url as such:
```
$ 'https://dash-boulder.plotly.host/YOUR_APP_NAME/boulder' or 'https://dash-boulder.plotly.host/YOUR_APP_NAME/denver'
```
## Dash Enterprise Debugging Tips
- Dash Enterprise currently requires Linux or Windows OS in order to push to their repo
- Error codes relating to certificates try the following. 
```
sudo apt-get install --reinstall ca-certificates
```
```
sudo dpkg --configure -a
```
```
sudo mkdir /usr/local/share/ca-certificates/cacert.org
```
```
sudo wget -P /usr/local/share/ca-certificates/cacert.org http://www.cacert.org/certs/root.crt http://www.cacert.org/certs/class3.crt
```
```
sudo update-ca-certificates
```
```
git config --global http.sslCAinfo /etc/ssl/certs/ca-certificates.crt
```
```
