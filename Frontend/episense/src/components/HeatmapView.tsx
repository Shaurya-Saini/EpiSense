import React, { useEffect, useMemo } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap, CircleMarker } from "react-leaflet";
import L from "leaflet";
import "leaflet.heat";

// Dummy coordinates for the zones since they are hardcoded
const ZONE_COORDS: Record<string, [number, number]> = {
  "zone_001": [28.6139, 77.2090], // e.g. center
  "zone_002": [28.7041, 77.1025], // north
  "zone_003": [28.5355, 77.2618], // south
};

function HeatmapLayer({ dataPoints }: { dataPoints: [number, number, number][] }) {
  const map = useMap();
  const heatRef = React.useRef<any>(null);

  useEffect(() => {
    // Check if L.heatLayer is available (added by leaflet.heat)
    if (!(L as any).heatLayer) return;

    if (!heatRef.current) {
        heatRef.current = (L as any).heatLayer(dataPoints, {
          radius: 40,
          blur: 25,
          maxZoom: 17,
          gradient: { 0.4: 'blue', 0.6: 'cyan', 0.7: 'lime', 0.8: 'yellow', 1.0: 'red' }
        }).addTo(map);
    } else {
        heatRef.current.setLatLngs(dataPoints);
    }
    
    // Do not remove layer on unmount unless completely unmounting component
    return () => {
      // We keep it persistent across re-renders
    };
  }, [map, dataPoints]);

  return null;
}

export default function HeatmapView({ zoneUpdates }: { zoneUpdates: Record<string, any> }) {
  
  // Convert zoneUpdates into [lat, lng, intensity]
  const dataPoints = useMemo(() => {
    return Object.values(zoneUpdates).map(update => {
       const coords = ZONE_COORDS[update.zone_id] || [28.6139, 77.2090];
       // clamp intensity between 0 and 1
       const intensity = Math.min(Math.max(update.ori || 0, 0), 1);
       return [...coords, intensity] as [number, number, number];
    });
  }, [zoneUpdates]);

  return (
    <MapContainer center={[28.6139, 77.2090]} zoom={10} style={{ height: "100%", width: "100%" }} scrollWheelZoom={false}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
      />
      <HeatmapLayer dataPoints={dataPoints} />
      
      {/* Markers for the Zones */}
      {Object.values(zoneUpdates).map(update => {
         const coords = ZONE_COORDS[update.zone_id] || [28.6139, 77.2090];
         return (
            <CircleMarker key={update.zone_id} center={coords} radius={8} pathOptions={{ color: 'red', fillColor: '#f03', fillOpacity: 0.5 }}>
               <Popup>
                  <strong>{update.zone_id}</strong><br/>
                  ORI: {update.ori?.toFixed(2)}<br/>
                  Status: {update.alerts?.level || "Normal"}
               </Popup>
            </CircleMarker>
         );
      })}
    </MapContainer>
  );
}
