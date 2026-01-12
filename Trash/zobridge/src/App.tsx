import React from "react";
import { BrowserRouter, Route, Routes, Link } from "react-router-dom";
import Home from "./pages/Home";
import Feed from "./pages/feed";

/**
 * Main SPA application component. Backend router is defined in `../server.ts`.
 */
export default function App() {
  return (
    <BrowserRouter>
      <nav style={{ padding: 12, borderBottom: "1px solid #ddd" }}>
        <Link to="/">Home</Link> | <Link to="/feed">Feed</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/feed" element={<Feed />} />
        <Route path="/hello-zo-example" element={<div>Hi Zo</div>} />
      </Routes>
    </BrowserRouter>
  );
}
