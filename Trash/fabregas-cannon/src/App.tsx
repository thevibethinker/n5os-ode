import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import MeetingsList from "./pages/MeetingsList";
import MeetingDetail from "./pages/MeetingDetail";
import { ThemeProvider } from "@/components/theme-provider";

export default function App() {
  return (
    <ThemeProvider defaultTheme="dark">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MeetingsList />} />
          <Route path="/meeting/:id" element={<MeetingDetail />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

