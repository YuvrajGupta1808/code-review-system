/**
 * Main application component - orchestrates the IDE UI
 */

import { useEffect } from "react";
import { useStore } from "./store";
import { useMockEvents } from "./hooks/useMockEvents";
import { HomeScreen } from "./components/HomeScreen";
import { IDEInterface } from "./components/IDEInterface";

function App() {
  const { theme, uiMode } = useStore();

  // Set initial theme
  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    }
  }, [theme]);

  // SSE integration: we want the real backend by default.
  // (Mock events are still useful for local UI testing when the backend isn't running.)
  const useMock = false;
  useMockEvents(useMock);

  return <>{uiMode === "home" ? <HomeScreen /> : <IDEInterface />}</>;
}

export default App;
