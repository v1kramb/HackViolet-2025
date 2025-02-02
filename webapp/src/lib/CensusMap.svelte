<script lang="ts">
  import { Deck, FlyToInterpolator, Layer, LinearInterpolator } from '@deck.gl/core';
  import type { MapViewState, PickingInfo, ViewStateMap } from '@deck.gl/core';
  import { GeoJsonLayer, PolygonLayer, ScatterplotLayer, TextLayer } from '@deck.gl/layers';
  // import { DataFilterExtension } from '@deck.gl/extensions';
  // import type { DataFilterExtensionProps } from '@deck.gl/extensions';

  import { nameToAbbrev } from './name_to_abbrev';

  import CountyGeoJson from '$lib/data/counties.geojson?url';
  import StateGeoJson from '$lib/data/states.geojson?url';
  import type { Feature, FeatureCollection, Geometry, MultiPolygon } from 'geojson';

  import Color from 'color';
  import type { CensusData, CountyData } from '../routes/api/census_data/+server';

  let tooltip: HTMLDivElement;

  let {
    selectedCounty = $bindable(),
    censusData,
    countyTags,
    legislativeData,
    stateTags,
  }: {
    selectedCounty: {
      county: string;
      state: string;
    };
    censusData: CensusData;
    countyTags: string[];
    stateTags: string[];
    legislativeData: Record<Record<string, { description: string; fill: number }>>;
  } = $props();

  const INITIAL_VIEW_STATE: MapViewState = {
    latitude: 40,
    longitude: -96,
    zoom: 4,
    minZoom: 3.5,
    maxZoom: 8,
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

  let tooltipText: string = $state('');

  const updateTooltip = (
    { object, x, y }: PickingInfo<Feature<Geometry, CountyPropertiesTypes>>,
    text: string,
  ) => {
    if (object) {
      tooltip.style.display = 'block';
      tooltip.style.left = `${x}px`;
      tooltip.style.transform = 'translate(-50%, -120%)';
      tooltip.style.top = `${y}px`;
      tooltipText = text;
    } else {
      tooltip.style.display = 'none';
    }
  };

  let selectedState: string | null = null;

  const clearSelected = () => {
    selectedState = null;
    tooltip.style.display = 'none';
    selectedCounty = { county: '', state: '' };
  };

  let visible = new Map<string, GeoJsonLayer<CountyPropertiesTypes>>();
  let preload = new Map<string, GeoJsonLayer<CountyPropertiesTypes>>();

  let vs: MapViewState = INITIAL_VIEW_STATE;

  let deckInstance: Deck;

  $effect(() => {
    if (stateTags) {
      if (!deckInstance) {
        return;
      }
      const old_layers = deckInstance.props.layers.slice();
      if (!old_layers || old_layers.length === 0) {
        return;
      }
      const filterLayers = old_layers.filter((layer) => {
        if (layer && (layer as Layer).id.includes('states-fill-layer')) {
          return false;
        }
        return true;
      });
      for (let i = 0; i < old_layers.length; i++) {
        if (!old_layers[i]) {
          continue;
        }
        old_layers[i] = old_layers[i]!.clone({});
      }
      deckInstance.setProps({ layers: filterLayers });
      setTimeout(() => {
        deckInstance.setProps({ layers: old_layers });
      }, 50);
    }
  });

  $effect(() => {
    if (countyTags) {
      if (!deckInstance) {
        return;
      }
      const old_layers = deckInstance.props.layers.slice();
      if (!old_layers || old_layers.length === 0) {
        return;
      }
      const filterLayers = old_layers.filter((layer) => {
        if (layer && (layer as Layer).id.includes('counties-layer-')) {
          return false;
        }
        return true;
      });
      for (let i = 0; i < old_layers.length; i++) {
        if (!old_layers[i]) {
          continue;
        }
        old_layers[i] = old_layers[i]!.clone({});
      }
      deckInstance.setProps({ layers: filterLayers });
      setTimeout(() => {
        deckInstance.setProps({ layers: old_layers });
      }, 50);
    }
  });

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
            getFillColor: (d) => {
              const data =
                censusData[d.properties.ste_name[0].toLowerCase() as keyof typeof nameToAbbrev][
                  d.properties.coty_name_long[0].toLowerCase()
                ].percentage;

              // console.log(tags.reduce((acc, tag) => acc + data[tag], 0) / tags.length);

              return colorLow
                .lch()
                .mix(
                  colorHigh.lch(),
                  countyTags.reduce((acc, tag) => acc + parseFloat(data[tag]), 0) /
                    countyTags.length,
                )
                .rgb()
                .array() as any;
            },
            getLineColor: [255, 255, 255],
            transitions: {
              opacity: {
                duration: 300,
                easing: (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
              },
            },
            onHover: (p) => p.object && updateTooltip(p, p.object.properties.coty_name_long[0]),
            onDrag: (p) => p.object && updateTooltip(p, p.object.properties.coty_name_long[0]),
            onDragStart: () => {
              clearSelected();
            },
            onClick: (pickable: PickingInfo<Feature<Geometry, CountyPropertiesTypes>>) => {
              let object = pickable.object;
              if (object) {
                selectedState = object.properties.ste_code[0];

                selectedCounty.county =
                  selectedCounty.county === object.properties.coty_name_long[0]
                    ? ''
                    : object.properties.coty_name_long[0];

                selectedCounty.state = object.properties.ste_name[0];

                let coord = selectedCounty.county
                  ? object.properties.geo_point_2d
                  : stateCenterMap.get(object.properties.ste_code[0]) ||
                    object.properties.geo_point_2d;

                const dist = Math.sqrt(
                  (coord.lon - vs.longitude) ** 2 + (coord.lat - vs.latitude) ** 2,
                );
                deckInstance.setProps({
                  initialViewState: {
                    ...INITIAL_VIEW_STATE,
                    longitude: coord.lon + (Math.random() - 0.5) / 100,
                    latitude: coord.lat,
                    zoom: selectedCounty.county ? 7 : 5.5,
                    transitionDuration: dist * 200,
                    transitionEasing: (x: number) =>
                      x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2,
                    transitionInterpolator: new LinearInterpolator([
                      'zoom',
                      'latitude',
                      'longitude',
                    ]),
                  },
                });
              }
            },
          }),
        );
        return acc;
      }, new Map<string, GeoJsonLayer<CountyPropertiesTypes>>());

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

      const colorLow = new Color(
        window.getComputedStyle(document.documentElement).getPropertyValue('--color-low'),
      );
      const colorHigh = new Color(
        window.getComputedStyle(document.documentElement).getPropertyValue('--color-high'),
      );

      const getStateColor = (stateCode: string) => {
        if (!legislativeData || !stateCode) return [200, 200, 200];

        // console.log(stateCode);

        let datas = stateTags.map((tag) => legislativeData[tag][stateCode]);

        // console.log(stateCode, datas)

        let score = 0;
        let a = 0;
        for (let data of datas) {
          if (!data) continue;
          score += data.score;
          a++;
        }

        if (a === 0) return [200, 200, 200]; // Default gray if no data

        const normalizedScore = score / a / 100; // Convert 0-100 to 0-1 scale
        return colorLow
          .lch()
          .mix(colorHigh.lch(), normalizedScore / datas.length)
          .rgb()
          .array();
      };

      const stateFillLayer = new GeoJsonLayer<StatePropertiesTypes>({
        id: 'states-fill-layer',
        opacity: 1,
        data: state_data,
        pickable: false,
        stroked: true,
        extruded: false,
        filled: true,
        getLineWidth: 20,
        lineWidthMinPixels: 1,
        getFillColor: (d) => getStateColor(nameToAbbrev[d.properties.ste_name[0]]) as any,
        getLineColor: [128, 255, 255],
        transitions: {
          getFillColor: {
            duration: 300,
            easing: (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
          },
        },
      });

      const stateTextLayer = new TextLayer<StatePropertiesTypes>({
        id: 'states-text-layer',
        data: state_data.features.map((d) => d.properties),
        pickable: false,
        getPosition: (d) => [d.geo_point_2d.lon, d.geo_point_2d.lat],
        getText: (d) => nameToAbbrev[d.ste_name[0]],
        getSize: 24,
        getColor: [255, 255, 255],
        sizeScale: 0.5,
        getAngle: 0,
        getTextAnchor: 'middle',
        getAlignmentBaseline: 'center',
        getPixelOffset: [0, 0],
        transitions: {
          getSize: {
            duration: 300,
            easing: (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
          },
        },
      });

      let transitionDone = false;
      let transitionTimeout: NodeJS.Timeout | null = null;

      const stateOutlineLayer = new GeoJsonLayer<StatePropertiesTypes>({
        id: 'states-outline-layer',
        opacity: 1,
        data: state_data,
        pickable: true,
        stroked: true,
        filled: true,
        getLineWidth: 20,
        lineWidthMinPixels: 1,
        getLineColor: [255, 255, 255],
        getFillColor: [0, 0, 0, 0],
        autoHighlight: true,
        highlightColor: [255, 255, 255, 128],
        onHover: (p) => {
          if (!p.object) return;
          console.log(p.object.properties)
          let state_info = stateTags.map(
            (tag) => legislativeData[tag][nameToAbbrev[p.object.properties.ste_name[0]]],
          );
          console.log(state_info);
          let state_text = state_info.map((info) => info.description).join('<br>');
          updateTooltip(p, state_text);
        },
        onDrag: (p) => {
          if (!p.object) return;
          let state_info = stateTags.map(
            (tag) => legislativeData[tag][nameToAbbrev[p.object.properties.ste_name[0]]],
          );
          let state_text = state_info.map((info) => info.description).join('<br>');
          updateTooltip(p, state_text);
        },
        onClick: ({ object }) => {
          selectedState = object.properties.ste_code[0];
          const dist = Math.sqrt(
            (object.properties.geo_point_2d.lon - vs.longitude) ** 2 +
              (object.properties.geo_point_2d.lat - vs.latitude) ** 2,
          );
          if (transitionTimeout) {
            clearTimeout(transitionTimeout);
          }
          transitionDone = false;
          transitionTimeout = setTimeout(() => {
            transitionDone = true;
            transitionTimeout = null;
          }, dist * 50);
          selectedCounty = { county: '', state: '' };
          deckInstance.setProps({
            initialViewState: {
              ...INITIAL_VIEW_STATE,
              longitude: object.properties.geo_point_2d.lon + (Math.random() - 0.5) / 100,
              latitude: object.properties.geo_point_2d.lat,
              zoom: 5.5,
              transitionDuration: dist * 50,
              transitionEasing: (x: number) =>
                x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2,
              transitionInterpolator: new LinearInterpolator(['zoom', 'latitude', 'longitude']),
            },
          });
        },
        onDragStart: () => {
          clearSelected();
        },
        transitions: {
          lineWidthMinPixels: {
            duration: 300,
            easing: (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
          },
        },
      });

      const loadStates = (viewState: MapViewState) => {
        const max_dist = (6 - Math.min(Math.max(viewState.zoom, 4.75), 5.25)) ** 2 * 50 + 15;
        const preload_dist = max_dist * 2;

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
          } else if (distance < preload_dist) {
            if (!preload.has(stateCode)) {
              preload.set(stateCode, stateCountyLayerMap.get(stateCode)!.clone({ opacity: 0 }));
            }
          }
        }

        visible.delete(selectedState || '');
      };

      const fullScreenPolygon = [
        [-180, -90],
        [180, -90],
        [180, 90],
        [-180, 90],
      ];

      const colorLayer = new PolygonLayer({
        id: 'background',
        opacity: 1,
        data: [
          {
            polygon: fullScreenPolygon,
          },
        ],
        getPolygon: (d) => d.polygon,
        stroked: false,
        filled: true,
        pickable: false,
        getFillColor: [32, 32, 128, 64],
        transitions: {
          opacity: {
            duration: 100,
            easing: (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
          },
        },
      });

      const updateLayers = () => {
        const colorLayerCopy = colorLayer.clone({
          opacity: selectedState === null ? 0 : 1,
        });
        if (vs.zoom > 4.75) {
          deckInstance.setProps({
            layers: [
              stateFillLayer,
              stateTextLayer,
              ...preload.values(),
              stateOutlineLayer.clone({
                lineWidthMinPixels: 2,
              }),
              ...visible.values(),
              colorLayerCopy,
              stateCountyLayerMap.get(selectedState || '')?.clone({
                pickable: true,
                onDragStart: () => {},
              }),
            ],
          });
        } else {
          deckInstance.setProps({
            layers: [
              stateFillLayer,
              ...[...preload.values()].map((e) =>
                e.clone({
                  opacity: 0,
                  pickable: false,
                }),
              ),
              stateTextLayer,
              ...[...visible.values()].map((e) =>
                e.clone({
                  opacity: 0,
                  pickable: false,
                }),
              ),
              stateOutlineLayer,
              colorLayerCopy,
              stateCountyLayerMap.get(selectedState || '')?.clone({
                pickable: true,
                onDragStart: () => {},
              }),
            ],
          });
        }
      };

      loadStates(INITIAL_VIEW_STATE);
      deckInstance = new Deck({
        canvas: 'deck-container',
        initialViewState: INITIAL_VIEW_STATE,
        controller: true,
        layers: [stateLayer, ...visible.values(), ...preload.values(), stateFillLayer],
        onViewStateChange: ({ viewState }) => {
          vs = viewState;
          if (transitionDone && viewState.zoom < 5.25) {
            clearSelected();
          }
          loadStates(viewState);
          updateLayers();
        },
      });
    })();
  });
</script>

<div class="absolute left-0 top-0 h-full w-full">
  <canvas id="deck-container"></canvas>
</div>

<div
  class="pointer-events-none absolute z-10 hidden rounded-3xl bg-white px-2 py-1 text-xs text-gray-700"
  bind:this={tooltip}
>
  {@html tooltipText}
</div>
