import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";

/**
 * Main SPA application component. Backend router is defined in `../server.ts`.
 */
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/hello-zo-example" element={<div>Hi Zo</div>} />
      </Routes>
    </BrowserRouter>
  );
}
