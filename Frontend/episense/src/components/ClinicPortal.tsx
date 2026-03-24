import React, { useState } from "react";
import { Link } from "react-router-dom";

const API_URL = "http://localhost:8000/api";

export default function ClinicPortal() {
  const [formData, setFormData] = useState({
    zone_id: "zone_001",
    population: 5000,
    fever: 0,
    diarrhea: 0,
    vomiting: 0,
    rash: 0,
    respiratory: 0
  });

  const [status, setStatus] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("Submitting...");
    
    try {
      const res = await fetch(`${API_URL}/symptom-report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
           zone_id: formData.zone_id,
           population: parseInt(formData.population as any, 10),
           fever: parseInt(formData.fever as any, 10),
           diarrhea: parseInt(formData.diarrhea as any, 10),
           vomiting: parseInt(formData.vomiting as any, 10),
           rash: parseInt(formData.rash as any, 10),
           respiratory: parseInt(formData.respiratory as any, 10),
        })
      });

      if (res.ok) {
        setStatus("Report Submitted Successfully!");
      } else {
        setStatus("Error: Could not submit report.");
      }
    } catch (err) {
      console.error(err);
      setStatus("Error: Server unreachable.");
    }
  };

  return (
    <div className="clinic-portal">
      <div style={{ maxWidth: "800px", margin: "0 auto" }}>
         <Link to="/" className="back-link">← Back to Dashboard</Link>
         
         <div className="portal-container">
            <h1 className="portal-title">Clinical Symptom Ingestion Portal</h1>
            <div className="portal-badge">Restricted Access: Authorized Clinics & Hospitals Only</div>
            
            <div className="explainer-card">
               <h3>What is this portal for?</h3>
               <p>
                 This portal integrates localized clinical data into the EpiSense **Outbreak Risk Index (ORI)**. 
                 By submitting aggregated symptom reports, your clinic provides the human health signals 
                 needed to cross-reference environmental contamination data (water quality, temperature).
               </p>
               <h3>How it works</h3>
               <p>
                 When you submit a symptom report, the system calculates a <strong>Symptom Burden Score (S_Score)</strong>. 
                 This score is combined with the Environmental Score (E_Score) from the IoT sensors to produce the unified ORI.
                 If the combined risk crosses a public health threshold, early-warning alerts are generated system-wide.
               </p>
               <h3>How to input values</h3>
               <ul>
                  <li><strong>Zone / Ward:</strong> Select the geographical area your clinic covers.</li>
                  <li><strong>Population Covered:</strong> Estimate the total number of people routinely serviced by your clinic in that zone.</li>
                  <li><strong>Symptom Cases:</strong> Enter the exact number of new patients presenting with each listed symptom over the past 24 hours. Enter '0' if none.</li>
               </ul>
            </div>
            
            <form onSubmit={handleSubmit} className="portal-form">
               <div className="form-group">
                  <label>Service Zone / Ward</label>
                  <select name="zone_id" value={formData.zone_id} onChange={handleChange} required>
                     <option value="zone_001">Zone 001 (Center)</option>
                     <option value="zone_002">Zone 002 (North)</option>
                     <option value="zone_003">Zone 003 (South)</option>
                  </select>
               </div>

               <div className="form-group">
                  <label>Total Population Covered</label>
                  <input type="number" name="population" value={formData.population} onChange={handleChange} min="1" required />
               </div>
               
               <fieldset className="symptom-fieldset">
                  <legend>New Symptom Cases (Last 24h)</legend>
                  
                  <div className="symptom-grid">
                     <div className="symptom-input">
                        <label>Fever</label>
                        <input type="number" name="fever" value={formData.fever} onChange={handleChange} min="0" required />
                     </div>
                     <div className="symptom-input">
                        <label>Diarrhea</label>
                        <input type="number" name="diarrhea" value={formData.diarrhea} onChange={handleChange} min="0" required />
                     </div>
                     <div className="symptom-input">
                        <label>Vomiting</label>
                        <input type="number" name="vomiting" value={formData.vomiting} onChange={handleChange} min="0" required />
                     </div>
                     <div className="symptom-input">
                        <label>Rash</label>
                        <input type="number" name="rash" value={formData.rash} onChange={handleChange} min="0" required />
                     </div>
                     <div className="symptom-input">
                        <label>Respiratory Distress</label>
                        <input type="number" name="respiratory" value={formData.respiratory} onChange={handleChange} min="0" required />
                     </div>
                  </div>
               </fieldset>

               <button type="submit" className="submit-btn" disabled={status === "Submitting..."}>
                  {status === "Submitting..." ? "Processing..." : "Submit Clinical Report"}
               </button>
               
               {status && status !== "Submitting..." && (
                  <div className={`status-message ${status.includes("Error") ? "error" : "success"}`}>
                     {status}
                  </div>
               )}
            </form>
         </div>
      </div>
    </div>
  );
}
