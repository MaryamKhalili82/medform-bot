import React from "react";
import Chatbot from "./Chatbot";

const PatientPage = () => {
  const medicalRequestFormId = 63;
  console.log("📤 Sending form ID to Chatbot:", medicalRequestFormId);

  return (
    <div style={{ padding: "20px" }}>
      <h1>🩺 Patient Record Page</h1>
      <p><strong>Medical Request Form ID:</strong> {medicalRequestFormId}</p>
      <Chatbot medicalRequestFormId={medicalRequestFormId} />
    </div>
  );
};

export default PatientPage;