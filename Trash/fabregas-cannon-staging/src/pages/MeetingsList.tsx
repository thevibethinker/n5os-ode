import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Calendar,
  FileText,
  Search,
  RefreshCw,
  Eye,
  EyeOff,
  Check,
  Circle,
  Mail,
  Users,
  MessageSquare,
  Clock,
  AlertTriangle,
  AlertCircle,
} from "lucide-react";

interface Meeting {
  id: string;
  folder: string;
  date: string;
  title: string;
  status: string;
  meeting_type: string;
  cloaked: boolean;
  blocks: string[];
  has_transcript: boolean;
  done: boolean;
  tags: string[];
  needs_followup_email: boolean;
  needs_deliverables: boolean;
  needs_warm_intro: boolean;
  needs_blurb: boolean;
  days_since_meeting: number;
}

export default function MeetingsList() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [doneFilter, setDoneFilter] = useState("all");
  const [urgencyFilter, setUrgencyFilter] = useState("all");

  const fetchMeetings = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/meetings");
      const data = await res.json();
      setMeetings(data.meetings || []);
    } catch (error) {
      console.error("Failed to fetch meetings:", error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchMeetings();
  }, []);

  const toggleDone = async (e: React.MouseEvent, meeting: Meeting) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await fetch(`/api/meetings/${meeting.id}/done`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ done: !meeting.done }),
      });
      setMeetings(meetings.map(m => 
        m.id === meeting.id ? { ...m, done: !m.done } : m
      ));
    } catch (error) {
      console.error("Failed to toggle done:", error);
    }
  };

  const cloakMeeting = async (e: React.MouseEvent, meetingId: string) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await fetch(`/api/meetings/${meetingId}/cloak`, { method: "POST" });
      setMeetings(meetings.filter((m) => m.id !== meetingId));
    } catch (error) {
      console.error("Failed to cloak meeting:", error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "processed":
        return "bg-emerald-900/50 text-emerald-300 border border-emerald-700";
      case "processing":
      case "mid_processing":
        return "bg-amber-900/50 text-amber-300 border border-amber-700 animate-pulse";
      case "pending":
        return "bg-zinc-800 text-zinc-400 border border-zinc-700";
      default:
        return "bg-zinc-800 text-zinc-400 border border-zinc-700";
    }
  };

  const getUrgencyIndicator = (meeting: Meeting) => {
    if (meeting.done) return null;
    
    const hasActions = meeting.needs_followup_email || meeting.needs_deliverables || 
                       meeting.needs_warm_intro || meeting.needs_blurb;
    
    if (!hasActions) return null;
    
    if (meeting.days_since_meeting >= 7) {
      return (
        <div className="flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-red-900/70 text-red-200 border border-red-600 animate-pulse">
          <AlertCircle size={12} />
          <span>{meeting.days_since_meeting}d overdue</span>
        </div>
      );
    }
    
    if (meeting.days_since_meeting >= 2) {
      return (
        <div className="flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-amber-900/60 text-amber-200 border border-amber-600">
          <AlertTriangle size={12} />
          <span>{meeting.days_since_meeting}d ago</span>
        </div>
      );
    }
    
    return (
      <div className="flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-zinc-800 text-zinc-400">
        <Clock size={12} />
        <span>{meeting.days_since_meeting}d</span>
      </div>
    );
  };

  const getActionIndicators = (meeting: Meeting) => {
    if (meeting.done) return null;
    
    const indicators = [];
    
    if (meeting.needs_followup_email) {
      indicators.push(
        <div key="email" className="flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-blue-900/50 text-blue-300 border border-blue-700" title="Follow-up email needed">
          <Mail size={10} />
          <span>Email</span>
        </div>
      );
    }
    
    if (meeting.needs_warm_intro) {
      indicators.push(
        <div key="intro" className="flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-purple-900/50 text-purple-300 border border-purple-700" title="Warm intro needed">
          <Users size={10} />
          <span>Intro</span>
        </div>
      );
    }
    
    if (meeting.needs_blurb) {
      indicators.push(
        <div key="blurb" className="flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-cyan-900/50 text-cyan-300 border border-cyan-700" title="Blurb needed">
          <MessageSquare size={10} />
          <span>Blurb</span>
        </div>
      );
    }
    
    if (meeting.needs_deliverables) {
      indicators.push(
        <div key="deliverable" className="flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-orange-900/50 text-orange-300 border border-orange-700" title="Deliverables due">
          <FileText size={10} />
          <span>Action</span>
        </div>
      );
    }
    
    return indicators.length > 0 ? (
      <div className="flex flex-wrap gap-1">
        {indicators}
      </div>
    ) : null;
  };

  // Filter meetings
  const filteredMeetings = meetings.filter((m) => {
    if (search && !m.title.toLowerCase().includes(search.toLowerCase()) && 
        !m.folder.toLowerCase().includes(search.toLowerCase())) {
      return false;
    }
    if (typeFilter !== "all" && m.meeting_type !== typeFilter) return false;
    if (statusFilter !== "all" && m.status !== statusFilter) return false;
    if (doneFilter === "done" && !m.done) return false;
    if (doneFilter === "undone" && m.done) return false;
    
    // Urgency filter
    if (urgencyFilter === "critical" && (m.done || m.days_since_meeting < 7)) return false;
    if (urgencyFilter === "warning" && (m.done || m.days_since_meeting < 2 || m.days_since_meeting >= 7)) return false;
    if (urgencyFilter === "has_actions") {
      const hasActions = m.needs_followup_email || m.needs_deliverables || m.needs_warm_intro || m.needs_blurb;
      if (!hasActions || m.done) return false;
    }
    
    return true;
  });

  const uniqueStatuses = [...new Set(meetings.map((m) => m.status))];
  
  // Stats
  const undoneWithActions = meetings.filter(m => 
    !m.done && (m.needs_followup_email || m.needs_deliverables || m.needs_warm_intro || m.needs_blurb)
  ).length;
  const criticalCount = meetings.filter(m => !m.done && m.days_since_meeting >= 7 && 
    (m.needs_followup_email || m.needs_deliverables || m.needs_warm_intro || m.needs_blurb)
  ).length;
  const processingCount = meetings.filter(m => m.status === "processing" || m.status === "mid_processing").length;

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#1a0f0a' }}>
      <main className="max-w-6xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <img 
              src="/n5-badge.webp" 
              alt="N5 OS" 
              className="w-14 h-14 object-contain"
            />
            <div>
              <h1 className="text-2xl font-bold" style={{ color: '#F5B941' }}>
                Fabregas Cannon
              </h1>
              <p className="text-sm italic" style={{ color: '#D4A574' }}>
                Victory Through Email Velocity
              </p>
            </div>
          </div>
          <Button
            onClick={fetchMeetings}
            variant="outline"
            size="sm"
            className="gap-2"
            style={{ borderColor: '#D4A574', color: '#D4A574' }}
          >
            <RefreshCw size={14} />
            Refresh
          </Button>
        </div>

        {/* Stats Bar */}
        <div className="flex gap-4 mb-4 text-sm" style={{ color: '#D4A574' }}>
          {criticalCount > 0 && (
            <div className="flex items-center gap-1 px-3 py-1 rounded bg-red-900/50 border border-red-700 text-red-300">
              <AlertCircle size={14} />
              <span>{criticalCount} critical (7d+)</span>
            </div>
          )}
          {undoneWithActions > 0 && (
            <div className="flex items-center gap-1 px-3 py-1 rounded" style={{ backgroundColor: 'rgba(139, 58, 31, 0.3)', borderColor: '#8B3A1F', border: '1px solid' }}>
              <span>{undoneWithActions} need action</span>
            </div>
          )}
          {processingCount > 0 && (
            <div className="flex items-center gap-1 px-3 py-1 rounded bg-amber-900/30 border border-amber-700 text-amber-300">
              <span>{processingCount} processing</span>
            </div>
          )}
        </div>

        {/* Search and Filters */}
        <div className="flex flex-wrap gap-3 mb-6">
          <div className="relative flex-1 min-w-[200px]">
            <Search
              className="absolute left-3 top-1/2 transform -translate-y-1/2"
              size={16}
              style={{ color: '#8B3A1F' }}
            />
            <Input
              placeholder="Search meetings..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10 h-9 text-sm"
              style={{ backgroundColor: '#2C1810', borderColor: '#5C2E1A', color: '#FFF8F0' }}
            />
          </div>

          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-[120px] h-9 text-sm" style={{ backgroundColor: '#2C1810', borderColor: '#5C2E1A', color: '#D4A574' }}>
              <SelectValue placeholder="Type" />
            </SelectTrigger>
            <SelectContent style={{ backgroundColor: '#2C1810', borderColor: '#5C2E1A' }}>
              <SelectItem value="all" className="text-[#D4A574]">All Types</SelectItem>
              <SelectItem value="external" className="text-[#D4A574]">External</SelectItem>
              <SelectItem value="internal" className="text-[#D4A574]">Internal</SelectItem>
            </SelectContent>
          </Select>

          <Select value={doneFilter} onValueChange={setDoneFilter}>
            <SelectTrigger className="w-[120px] h-9 text-sm" style={{ backgroundColor: '#2C1810', borderColor: '#5C2E1A', color: '#D4A574' }}>
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent style={{ backgroundColor: '#2C1810', borderColor: '#5C2E1A' }}>
              <SelectItem value="all" className="text-[#D4A574]">All</SelectItem>
              <SelectItem value="undone" className="text-[#D4A574]">Undone</SelectItem>
              <SelectItem value="done" className="text-[#D4A574]">Done</SelectItem>
            </SelectContent>
          </Select>

          <Select value={urgencyFilter} onValueChange={setUrgencyFilter}>
            <SelectTrigger className="w-[140px] h-9 text-sm" style={{ backgroundColor: '#2C1810', borderColor: '#5C2E1A', color: '#D4A574' }}>
              <SelectValue placeholder="Urgency" />
            </SelectTrigger>
            <SelectContent style={{ backgroundColor: '#2C1810', borderColor: '#5C2E1A' }}>
              <SelectItem value="all" className="text-[#D4A574]">All</SelectItem>
              <SelectItem value="has_actions" className="text-[#D4A574]">Needs Action</SelectItem>
              <SelectItem value="warning" className="text-[#D4A574]">⚠️ 2-6 days</SelectItem>
              <SelectItem value="critical" className="text-[#D4A574]">🚨 7+ days</SelectItem>
            </SelectContent>
          </Select>

          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[130px] h-9 text-sm" style={{ backgroundColor: '#2C1810', borderColor: '#5C2E1A', color: '#D4A574' }}>
              <SelectValue placeholder="Processing" />
            </SelectTrigger>
            <SelectContent style={{ backgroundColor: '#2C1810', borderColor: '#5C2E1A' }}>
              <SelectItem value="all" className="text-[#D4A574]">All Statuses</SelectItem>
              {uniqueStatuses.map((s) => (
                <SelectItem key={s} value={s} className="text-[#D4A574]">
                  {s}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Meetings count */}
        <p className="text-sm mb-4" style={{ color: '#8B3A1F' }}>
          Showing {filteredMeetings.length} of {meetings.length} meetings
        </p>

        {/* Meetings List */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="animate-spin" size={24} style={{ color: '#D4A574' }} />
          </div>
        ) : filteredMeetings.length === 0 ? (
          <div className="text-center py-12" style={{ color: '#8B3A1F' }}>
            No meetings found
          </div>
        ) : (
          <div className="space-y-2">
            {filteredMeetings.map((meeting) => (
              <Link key={meeting.id} to={`/meeting/${meeting.id}`}>
                <Card
                  className="transition-all duration-200 hover:scale-[1.01]"
                  style={{
                    backgroundColor: meeting.done ? 'rgba(44, 24, 16, 0.5)' : '#2C1810',
                    borderColor: meeting.days_since_meeting >= 7 && !meeting.done ? '#dc2626' : 
                                 meeting.days_since_meeting >= 2 && !meeting.done ? '#d97706' : '#5C2E1A',
                    borderWidth: meeting.days_since_meeting >= 7 && !meeting.done ? '2px' : '1px',
                    opacity: meeting.done ? 0.7 : 1,
                  }}
                >
                  <CardContent className="py-3 px-4">
                    <div className="flex items-center justify-between gap-4">
                      {/* Left: Done toggle + Title */}
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <button
                          onClick={(e) => toggleDone(e, meeting)}
                          className="flex-shrink-0 p-1 rounded hover:bg-white/10 transition-colors"
                          title={meeting.done ? "Mark as undone" : "Mark as done"}
                        >
                          {meeting.done ? (
                            <Check size={18} style={{ color: '#10b981' }} />
                          ) : (
                            <Circle size={18} style={{ color: '#5C2E1A' }} />
                          )}
                        </button>
                        <div className="min-w-0 flex-1">
                          <h3 
                            className={`font-medium truncate ${meeting.done ? 'line-through' : ''}`}
                            style={{ color: meeting.done ? '#8B3A1F' : '#FFF8F0' }}
                          >
                            {meeting.title}
                          </h3>
                          <div className="flex items-center gap-3 text-xs mt-1" style={{ color: '#8B3A1F' }}>
                            <span className="flex items-center gap-1">
                              <Calendar size={10} />
                              {meeting.date}
                            </span>
                            <span>{meeting.meeting_type}</span>
                            <span>{meeting.blocks.length} blocks</span>
                          </div>
                        </div>
                      </div>

                      {/* Right: Action indicators + Urgency + Status + Cloak */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {getActionIndicators(meeting)}
                        {getUrgencyIndicator(meeting)}
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(meeting.status)}`}>
                          {meeting.status}
                        </span>
                        <button
                          onClick={(e) => cloakMeeting(e, meeting.id)}
                          className="p-1.5 rounded hover:bg-white/10 transition-colors"
                          title="Cloak this meeting"
                        >
                          <EyeOff size={14} style={{ color: '#5C2E1A' }} />
                        </button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}

        {/* Footer */}
        <footer className="mt-12 pt-6 border-t" style={{ borderColor: '#5C2E1A' }}>
          <p className="text-center text-sm" style={{ color: '#8B3A1F' }}>
            Powered by <span style={{ color: '#F5B941', fontWeight: 600 }}>N5 OS</span> • Built on Zo Computer
          </p>
        </footer>
      </main>
    </div>
  );
}

