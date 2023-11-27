## NPM Influx Exporter

#### Export NGINX Proxy Manager access to logs InfluxDB

### Features

- Lightweight docker image (~85 MB)
- Runs with limited memory (< 100 MB)
- Geolocation caching for faster lookups

### Installation

Generate a [MaxMind license key](https://support.maxmind.com/hc/en-us/articles/4407111582235-Generate-a-License-Key) to download the database to geolocate IP addresses.

Create a `.env` file with at minimum the following;

```
DEBUG=false

INFLUX_URL=http://<influx host>:<influx port>
INFLUX_ORG=<influx org>
INFLUX_BUCKET=<influx bucket>
INFLUX_TOKEN=<influx bucket>

GEOIPUPDATE_ACCOUNT_ID=<MaxMind account ID>
GEOIPUPDATE_LICENSE_KEY=<MaxMind license key>
```

> Running with `DEBUG=true` will generate lots of log output.

Copy the `docker-compose.yml` file to your directory and populate with the correct paths

Run `docker-compose up -d`

### Grafana

This project was heavily inspired by [smilebeast](https://github.com/smilebasti/npmGrafStats) who created a Grafana  dashboard available [here](https://grafana.com/grafana/dashboards/18826-npmgrafstats-map-dashboard-influx-v2-3/)

### Development

This project is created with Poetry.

1. Create a virtual environment
2. Install python dependecies with `poetry install`
3. Install pre-commit hooks with `pre-commit install`

Development dependencies can be installed with `poetry install --with dev`

### Testing

```bash
pytest
```
