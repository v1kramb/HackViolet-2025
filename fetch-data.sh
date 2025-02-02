#!/bin/bash

cd "$(dirname "$0")"
SCRIPT_DIR="$(pwd)"
echo "Script directory: $SCRIPT_DIR"

mkdir -p webapp/data

DATA_DIR="$SCRIPT_DIR/webapp/src/lib/data"

STATE_GEOJSON_NAME="states.geojson"
COUNTY_GEOJSON_NAME="counties.geojson"

# https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/georef-united-states-of-america-state/exports/geojson?lang=en&timezone=America%2FNew_York
if [ ! -f $DATA_DIR/$STATE_GEOJSON_NAME ]; then
  echo "Downloading $STATE_GEOJSON_NAME"
  curl -o $DATA_DIR/$STATE_GEOJSON_NAME "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/georef-united-states-of-america-state/exports/geojson?lang=en&timezone=America%2FNew_York"
else
  echo "File $STATE_GEOJSON_NAME already exists"
fi


# # check if file doesnt exists
if [ ! -f $DATA_DIR/$COUNTY_GEOJSON_NAME ]; then
  echo "Downloading $COUNTY_GEOJSON_NAME"
  curl -o $DATA_DIR/$COUNTY_GEOJSON_NAME "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/georef-united-states-of-america-county/exports/geojson?lang=en&timezone=America%2FNew_York"
else
  echo "File $COUNTY_GEOJSON_NAME already exists"
fi



echo "Done"
