

import React, { useState, useRef } from "react";
import axios from "axios";

const Chatbot = ({ medicalRequestFormId }) => {
  const [recognizedText, setRecognizedText] = useState("");
  const [confirmedTests, setConfirmedTests] = useState([]);
  const confirmedTestsRef = useRef([]);
  const [confirmation, setConfirmation] = useState("");
  const [showSessionOptions, setShowSessionOptions] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [recognizing, setRecognizing] = useState(false);

  const startListening = () => {
    const recognition = new window.webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      setRecognizing(true);
      setRecognizedText("");
      setStatusMessage("");
      setConfirmation("");
      console.log("🎙️ Listening for multiple test names...");
    };

    recognition.onresult = async (event) => {
      const transcript = event.results[0][0].transcript;
      console.log("🎤 Recognized speech:", transcript);
      setRecognizedText(transcript);
      try {
        const response = await axios.post("http://127.0.0.1:8000/process", {
          text: transcript,
          speech: true,
        });
        console.log("🟢 Backend Response:", response.data);
        const confirmed = response.data.confirmedTest || [];

        setConfirmedTests(prev => [...new Set([...prev, ...confirmed])]);
        confirmedTestsRef.current = [...new Set([...confirmedTestsRef.current, ...confirmed])];
      } catch (error) {
        console.error("❌ Error sending request:", error);
      } finally {
        setRecognizing(false);
        console.log("🛑 Finished listening.");
      }
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setRecognizing(false);
    };

    recognition.start();
  };

  const confirmTests = async () => {
    setStatusMessage("⏳ Confirming the Tests...");
    const payload = {
      tests: confirmedTestsRef.current,
      medical_request_form_id: parseInt(medicalRequestFormId),
    };
    console.log("📦 Final payload being sent:", payload);
    try {
      const response = await axios.post("http://127.0.0.1:8000/finalize", payload);
      console.log("✅ POST Success:", response.data);
      setStatusMessage("✅ Tests are confirmed.");
      if (response.status === 200) {
        const testList = confirmedTestsRef.current.join(", ");
        setConfirmation([
          
          "✅ Medical Test Requisition Form Updated.",
          
          `Confirmed tests: ${testList}`,
          "🩺 Would you like to close the session for this patient?"
        ].join("\n"));
        setShowSessionOptions(true);
      }
    } catch (error) {
      console.error("❌ Error confirming tests:", error);
      setStatusMessage("");
    }
  };

  return (
    <div className="chatbot-container">
      <h2>Voice Medical Chatbot</h2>
      <input
        type="text"
        value={recognizedText}
        readOnly
        placeholder="Recognized speech will appear here"
        style={{ width: "100%", marginBottom: "1em" }}
      />
      <div>
        <button onClick={startListening} disabled={recognizing}>
          {recognizing ? "Listening..." : "Start Speaking"}
        </button>
        <button
          onClick={confirmTests}
          disabled={confirmedTests.length === 0 || !medicalRequestFormId}
        >
          Confirm
        </button>
      </div>

      {statusMessage && (
        <div style={{ marginTop: "1em", color: "#333", fontStyle: "italic" }}>
          {statusMessage}
        </div>
      )}

      {confirmation && (
        <div style={{ marginTop: "1em", color: "green", fontWeight: "bold", whiteSpace: "pre-line" }}>
          {confirmation}
        </div>
      )}

      {confirmedTests.length > 0 && (
        <div style={{ marginTop: "1em" }}>
          <strong>Detected Tests:</strong>
          <ul>
            {confirmedTests.map((test, index) => (
              <li key={index}>{test}</li>
            ))}
          </ul>
        </div>
      )}

      {showSessionOptions && (
        <div className="session-options" style={{ marginTop: "1em" }}>
          <button
            onClick={() => {
              setConfirmedTests([]);
              setConfirmation("");
              setShowSessionOptions(false);
              setStatusMessage("🧘 Session closed. Ready for new patient.");
              setRecognizedText("");
            }}
          >
            ✅ Yes, close session
          </button>
          <button
            onClick={() => {
              setShowSessionOptions(false);
              setStatusMessage("🔄 Continuing current session.");
              // Confirmation and test list remain
            }}
          >
            ❌ No, continue
          </button>
        </div>
      )}
    </div>
  );
};

export default Chatbot;
