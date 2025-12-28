import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import Dash from "./pages/Dashboard";
import { ThemeProvider } from "@/components/theme-provider";

/**
 * Main SPA application component. Backend router is defined in `../server.ts`.
 */
export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dash />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

