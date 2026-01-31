
  import { createRoot } from "react-dom/client";
  import App from "./app/App.tsx";
  import "./styles/index.css";
  import { applySettings } from "./utils/applySettings";

  // Apply saved settings before rendering to avoid flash
  applySettings();

  createRoot(document.getElementById("root")!).render(<App />);
  