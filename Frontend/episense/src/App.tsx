import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import ClinicPortal from "./components/ClinicPortal";
import { AppProvider } from "./AppContext";
import "./App.css";
import "./index.css";
// Important: leaflet styles
import "leaflet/dist/leaflet.css";

function App() {
  return (
    <AppProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/clinic-upload" element={<ClinicPortal />} />
        </Routes>
      </Router>
    </AppProvider>
  );
}

export default App;
