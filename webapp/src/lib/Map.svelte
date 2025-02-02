<script lang="ts">
  import { Deck, FlyToInterpolator } from '@deck.gl/core';
  import type { MapViewState, ViewStateMap } from '@deck.gl/core';
  import { GeoJsonLayer, ScatterplotLayer } from '@deck.gl/layers';
  // import { DataFilterExtension } from '@deck.gl/extensions';
  // import type { DataFilterExtensionProps } from '@deck.gl/extensions';

  import CountyGeoJson from '$lib/data/counties.geojson?url';
  import StateGeoJson from '$lib/data/states.geojson?url';
  import type { Feature, FeatureCollection, Geometry, MultiPolygon } from 'geojson';

  const INITIAL_VIEW_STATE: MapViewState = {
    latitude: 40,
    longitude: -96,
    zoom: 4,
  };

  type StatePropertiesTypes = {
    geo_point_2d: { lon: number; lat: number };
    year: string;
    ste_code: string[];
    ste_name: string[];
    ste_area_code: string;
    ste_type: string;
    ste_name_long: string[];
    ste_fp_code: string;
    ste_gnis_code: string;
  };

  type CountyPropertiesTypes = {
    geo_point_2d: { lon: number; lat: number };
    year: string;
    ste_code: string[];
    ste_name: string[];
    coty_code: string[];
    coty_name: string[];
    coty_area_code: string;
    coty_type: string;
    coty_name_long: string[];
    coty_fp_code: string;
    coty_gnis_code: string;
  };

  $effect(() => {
    (async () => {
      const state_data: FeatureCollection<MultiPolygon, StatePropertiesTypes> = await (
        await fetch(StateGeoJson)
      ).json();
      const county_data: FeatureCollection<MultiPolygon, CountyPropertiesTypes> = await (
        await fetch(CountyGeoJson)
      ).json();

      const stateCenterMap: Map<string, { lon: number; lat: number }> = state_data.features.reduce(
        (acc, d) => {
          acc.set(d.properties.ste_code[0], d.properties.geo_point_2d);
          return acc;
        },
        new Map<string, { lon: number; lat: number }>(),
      );

      const stateLayer = new GeoJsonLayer<StatePropertiesTypes>({
        id: 'states-layer',
        data: state_data,
        pickable: false,
        stroked: false,
        extruded: false,
        filled: true,
        getLineWidth: 20,
        lineWidthMinPixels: 1,
        getFillColor: [255, 100, 100],
      });

      let selectedState: string = 'null';

      const stateOutlineLayer = new GeoJsonLayer<StatePropertiesTypes>({
        id: 'states-outline-layer',
        data: state_data,
        pickable: true,
        stroked: true,
        extruded: false,
        filled: true,
        getLineWidth: 20,
        lineWidthMinPixels: 1,
        getFillColor: [255, 100, 100],
        getLineColor: [255, 255, 255],
        autoHighlight: true,
        highlightColor: [255, 255, 255, 128],
        onClick: ({ object }) => {
          selectedState = object.properties.ste_code[0];
          deckInstance.setProps({
            initialViewState: {
              ...INITIAL_VIEW_STATE,
              longitude: object.properties.geo_point_2d.lon,
              latitude: object.properties.geo_point_2d.lat,
              zoom: 5.5,
              transitionInterpolator: new FlyToInterpolator({ speed: 2 }),
              transitionDuration: 'auto',
            },
          });
        },
        transitions: {
          lineWidthMinPixels: {
            duration: 300,
            easing: (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
          },
          getFillColor: {
            duration: 300,
            easing: (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
          },
        },
      });

      const stateCountyLayerMap: Map<
        string,
        GeoJsonLayer<CountyPropertiesTypes>
      > = state_data.features.reduce((acc, d) => {
        const stateCode = d.properties.ste_code[0];
        acc.set(
          stateCode,
          new GeoJsonLayer<CountyPropertiesTypes>({
            id: `counties-layer-${stateCode}`,
            data: county_data.features.filter((d) => d.properties.ste_code[0] === stateCode),
            opacity: 1,
            pickable: true,
            autoHighlight: true,
            highlightColor: [255, 255, 255, 128],
            stroked: true,
            extruded: false,
            filled: true,
            getLineWidth: 20,
            lineWidthMinPixels: 1,
            getPointRadius: 100,
            getFillColor: [255, 100, 100],
            getLineColor: [255, 200, 200],
            transitions: {
              opacity: {
                duration: 300,
                easing: (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
              },
            },
          }),
        );
        return acc;
      }, new Map<string, GeoJsonLayer<CountyPropertiesTypes>>());

      // console.log(...stateCountyLayerMap.values());

      let visible = new Map<string, GeoJsonLayer<CountyPropertiesTypes>>();
      let preload = new Map<string, GeoJsonLayer<CountyPropertiesTypes>>();

      const loadStates = (viewState: MapViewState) => {
        const max_dist = (6 - Math.min(Math.max(viewState.zoom, 4), 6)) ** 2 * 50 + 15;
        const preload_dist = max_dist + 10;

        for (const e of visible) {
          const distance =
            (stateCenterMap.get(e[0])!.lon - viewState.longitude) ** 2 +
            (stateCenterMap.get(e[0])!.lat - viewState.latitude) ** 2;
          if (distance >= max_dist) {
            preload.set(e[0], e[1].clone({ opacity: 0 }));
            visible.delete(e[0]);
          }
        }

        for (const e of preload) {
          const distance =
            (stateCenterMap.get(e[0])!.lon - viewState.longitude) ** 2 +
            (stateCenterMap.get(e[0])!.lat - viewState.latitude) ** 2;
          if (distance < max_dist) {
            visible.set(e[0], e[1].clone({ opacity: 1 }));
            preload.delete(e[0]);
          } else if (distance > preload_dist) {
            preload.delete(e[0]);
          }
        }

        for (const [stateCode, { lon, lat }] of stateCenterMap.entries()) {
          const distance = (lon - viewState.longitude) ** 2 + (lat - viewState.latitude) ** 2;
          if (distance < max_dist) {
            if (!visible.has(stateCode)) {
              visible.set(stateCode, stateCountyLayerMap.get(stateCode)!.clone({ opacity: 1 }));
            }
          } else if (distance < max_dist * 2) {
            if (!preload.has(stateCode)) {
              preload.set(stateCode, stateCountyLayerMap.get(stateCode)!.clone({ opacity: 0 }));
            }
          }
        }
      };

      const updateLayers = (layers: GeoJsonLayer[]) => {
        deckInstance.setProps({
          layers,
        });
      };

      loadStates(INITIAL_VIEW_STATE);
      const deckInstance = new Deck({
        canvas: 'deck-container',
        initialViewState: INITIAL_VIEW_STATE,
        controller: true,
        layers: [stateLayer, ...visible.values(), ...preload.values(), stateOutlineLayer],
        onViewStateChange: ({ viewState }) => {
          loadStates(viewState);
          if (viewState.zoom > 4.5) {
            updateLayers([
              stateLayer,
              ...visible.values(),
              ...preload.values(),
              stateOutlineLayer.clone({
                lineWidthMinPixels: 2,
                pickable: false,
                autoHighlight: false,
                getFillColor: [255, 100, 100, 0],
              }),
            ]);
          } else {
            updateLayers([stateLayer, ...visible.values(), ...preload.values(), stateOutlineLayer]);
          }
        },
      });
    })();
  });
</script>

<div class="absolute left-0 top-0 h-full w-full">
  <canvas id="deck-container"></canvas>
</div>
