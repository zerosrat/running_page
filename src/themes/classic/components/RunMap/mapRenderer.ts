import * as mapbox from 'react-map-gl/mapbox';
import * as maplibre from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import { MAPBOX_TOKEN } from '@/core/config';

// Keep all React controls/markers on the same renderer and context. Classic
// uses their shared public API; Mapbox remains available with an own token.
const renderer = MAPBOX_TOKEN ? mapbox : (maplibre as unknown as typeof mapbox);

export const { Layer, Source, FullscreenControl, NavigationControl, Marker } =
  renderer;
export default renderer.default;
export type { MapRef, MapInstance } from 'react-map-gl/mapbox';
