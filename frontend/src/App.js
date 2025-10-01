import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AssessmentProvider } from "@/context/AssessmentContext";

// Import pages
import { Onboarding } from "@/pages/Onboarding";
import { MemoryTest } from "@/pages/MemoryTest";
import { PatternTest } from "@/pages/PatternTest";
import { ClockTest } from "@/pages/ClockTest";
import { SpeechTest } from "@/pages/SpeechTest";
import { Results } from "@/pages/Results";

function App() {
  return (
    <div className="App">
      <AssessmentProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Onboarding />} />
            <Route path="/memory" element={<MemoryTest />} />
            <Route path="/pattern" element={<PatternTest />} />
            <Route path="/clock" element={<ClockTest />} />
            <Route path="/speech" element={<SpeechTest />} />
            <Route path="/results" element={<Results />} />
          </Routes>
        </BrowserRouter>
      </AssessmentProvider>
    </div>
  );
}

export default App;
