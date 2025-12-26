import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  ArrowLeft,
  FileText,
  Mail,
  Users,
  RefreshCw,
  Upload,
  Eye,
  EyeOff,
  CheckCircle,
  Clock,
  Loader2,
} from "lucide-react";
import ReactMarkdown from "react-markdown";

interface MeetingData {
  id: string;
  blocks: Record<string, string>;
  manifest: Record<string, unknown> | null;
  transcript: string | null;
  follow_up_email: string | null;
  files: string[];
}

interface ActionResult {
  success: boolean;
  action: string;
  conversation_id?: string;
  output?: string;
  error?: string;
}

export default function MeetingDetail() {
  const { id } = useParams<{ id: string }>();
  const [meeting, setMeeting] = useState<MeetingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [actionResult, setActionResult] = useState<ActionResult | null>(null);
  const [selectedBlock, setSelectedBlock] = useState<string | null>(null);

  const fetchMeeting = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/meetings/${id}`);
      const data = await res.json();
      setMeeting(data);
    } catch (error) {
      console.error("Failed to fetch meeting:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMeeting();
  }, [id]);

  const executeAction = async (action: string, params?: Record<string, string>) => {
    setActionLoading(action);
    setActionResult(null);
    try {
      const res = await fetch(`/api/meetings/${id}/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, ...params }),
      });
      const data = await res.json();
      setActionResult(data);
    } catch (error) {
      setActionResult({
        success: false,
        action,
        error: "Failed to execute action",
      });
    } finally {
      setActionLoading(null);
    }
  };

  const blockDisplayNames: Record<string, string> = {
    B01: "Detailed Recap",
    B02: "Commitments",
    B03: "Decisions / Stakeholder Intel",
    B05: "Action Items",
    B06: "Business Context",
    B07: "Tone & Context",
    B08: "Stakeholder Intelligence",
    B14: "Blurbs Requested",
    B21: "Key Moments",
    B25: "Deliverables",
    B26: "Meeting Metadata",
    B31: "Stakeholder Research",
  };

  const getBlockDisplayName = (filename: string) => {
    const match = filename.match(/^(B\d+)/);
    if (match && blockDisplayNames[match[1]]) {
      return blockDisplayNames[match[1]];
    }
    return filename.replace(/_/g, " ").replace(".md", "");
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#1a0f0a' }}>
        <RefreshCw className="w-8 h-8 animate-spin" style={{ color: '#F5B941' }} />
      </div>
    );
  }

  if (!meeting) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: '#1a0f0a' }}>
        <p style={{ color: '#D4A574' }}>Meeting not found</p>
      </div>
    );
  }

  const blockEntries = Object.entries(meeting.blocks);
  const manifest = meeting.manifest || {};

  return (
    <div className="min-h-screen" style={{ background: '#1a0f0a' }}>
      {/* N5 OS Header */}
      <header className="sticky top-0 z-10" style={{ 
        background: 'linear-gradient(135deg, #8B3A1F 0%, #5a1f11 100%)',
        borderBottom: '1px solid rgba(212, 165, 116, 0.3)'
      }}>
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link 
                to="/" 
                className="flex items-center gap-2 transition-colors"
                style={{ color: '#D4A574' }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#F5B941'}
                onMouseLeave={(e) => e.currentTarget.style.color = '#D4A574'}
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Back</span>
              </Link>
            </div>
            <div className="flex items-center gap-3">
              <img 
                src="/n5-badge.webp" 
                alt="N5 OS" 
                className="w-10 h-10 object-contain"
                style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' }}
              />
              <span className="font-semibold" style={{ color: '#F5B941' }}>N5 OS</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Meeting Title */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-2" style={{ color: '#FFF8F0' }}>
            {id?.replace(/_/g, " ").replace(/\[P\]$/, "").trim()}
          </h1>
          <div className="flex items-center gap-4">
            <Badge 
              variant="secondary"
              className="bg-[#D4A574]/20 text-[#F5B941] border border-[#D4A574]/30"
            >
              {(manifest.status as string) || "processed"}
            </Badge>
            <span className="text-sm" style={{ color: '#D4A574' }}>
              {(manifest.meeting_date as string) || ""}
            </span>
            <span className="text-sm" style={{ color: '#D4A574' }}>
              {blockEntries.length} intelligence blocks
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <Card className="mb-6" style={{ background: '#2C1810', border: '1px solid rgba(212, 165, 116, 0.2)' }}>
          <CardHeader>
            <CardTitle style={{ color: '#F5B941' }}>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Button
                onClick={() => executeAction("generate_follow_up")}
                disabled={actionLoading !== null}
                className="bg-gradient-to-r from-[#D4A574] to-[#F5B941] text-[#2C1810] font-semibold hover:from-[#F5B941] hover:to-[#D4A574]"
              >
                {actionLoading === "generate_follow_up" ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Mail className="w-4 h-4 mr-2" />
                )}
                Generate Follow-up
              </Button>
              <Button
                onClick={() => executeAction("generate_blurb")}
                disabled={actionLoading !== null}
                variant="outline"
                className="border-[#D4A574]/50 text-[#D4A574] hover:bg-[#8B3A1F]/30 hover:text-[#F5B941] hover:border-[#F5B941]"
              >
                {actionLoading === "generate_blurb" ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <FileText className="w-4 h-4 mr-2" />
                )}
                Generate Blurb
              </Button>
              <Button
                onClick={() => executeAction("generate_warm_intro")}
                disabled={actionLoading !== null}
                variant="outline"
                className="border-[#D4A574]/50 text-[#D4A574] hover:bg-[#8B3A1F]/30 hover:text-[#F5B941] hover:border-[#F5B941]"
              >
                {actionLoading === "generate_warm_intro" ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Users className="w-4 h-4 mr-2" />
                )}
                Warm Intro
              </Button>
              <Button
                onClick={() => executeAction("export_to_drive")}
                disabled={actionLoading !== null}
                variant="outline"
                className="border-[#D4A574]/50 text-[#D4A574] hover:bg-[#8B3A1F]/30 hover:text-[#F5B941] hover:border-[#F5B941]"
              >
                {actionLoading === "export_to_drive" ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Upload className="w-4 h-4 mr-2" />
                )}
                Export to Drive
              </Button>
            </div>

            {/* Action Result */}
            {actionResult && (
              <div 
                className="mt-4 p-4 rounded-lg"
                style={{ 
                  background: actionResult.success ? 'rgba(212, 165, 116, 0.1)' : 'rgba(220, 38, 38, 0.1)',
                  border: `1px solid ${actionResult.success ? 'rgba(212, 165, 116, 0.3)' : 'rgba(220, 38, 38, 0.3)'}`
                }}
              >
                <div className="flex items-center gap-2 mb-2">
                  {actionResult.success ? (
                    <CheckCircle className="w-5 h-5" style={{ color: '#F5B941' }} />
                  ) : (
                    <Clock className="w-5 h-5 text-red-400" />
                  )}
                  <span className="font-medium" style={{ color: actionResult.success ? '#F5B941' : '#ef4444' }}>
                    {actionResult.success ? "Action Triggered" : "Action Failed"}
                  </span>
                </div>
                {actionResult.conversation_id && (
                  <p className="text-sm" style={{ color: '#D4A574' }}>
                    Conversation: {actionResult.conversation_id}
                  </p>
                )}
                {actionResult.error && (
                  <p className="text-sm text-red-400">{actionResult.error}</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Content Tabs */}
        <Tabs defaultValue="blocks" className="w-full">
          <TabsList className="mb-4 bg-[#2C1810] border border-[#D4A574]/20">
            <TabsTrigger 
              value="blocks"
              className="data-[state=active]:bg-[#8B3A1F] data-[state=active]:text-[#F5B941] text-[#D4A574]"
            >
              Intelligence Blocks ({blockEntries.length})
            </TabsTrigger>
            <TabsTrigger 
              value="transcript"
              className="data-[state=active]:bg-[#8B3A1F] data-[state=active]:text-[#F5B941] text-[#D4A574]"
            >
              Transcript
            </TabsTrigger>
            <TabsTrigger 
              value="manifest"
              className="data-[state=active]:bg-[#8B3A1F] data-[state=active]:text-[#F5B941] text-[#D4A574]"
            >
              Manifest
            </TabsTrigger>
          </TabsList>

          <TabsContent value="blocks">
            <div className="grid gap-4">
              {/* Block regeneration buttons */}
              <Card style={{ background: '#2C1810', border: '1px solid rgba(212, 165, 116, 0.2)' }}>
                <CardHeader>
                  <CardTitle className="text-lg" style={{ color: '#F5B941' }}>Regenerate Blocks</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {["B01", "B02", "B03", "B05", "B06", "B07", "B08", "B14", "B21", "B25", "B26"].map((block) => (
                      <Button
                        key={block}
                        variant="outline"
                        size="sm"
                        onClick={() => executeAction("regenerate_block", { block })}
                        disabled={actionLoading !== null}
                        className="border-[#D4A574]/30 text-[#D4A574] hover:bg-[#8B3A1F]/30 hover:text-[#F5B941] hover:border-[#F5B941] text-xs"
                      >
                        {actionLoading === `regenerate_block_${block}` ? (
                          <Loader2 className="w-3 h-3 animate-spin" />
                        ) : (
                          block
                        )}
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Block list */}
              {blockEntries.map(([filename, content]) => (
                <Card 
                  key={filename} 
                  style={{ background: '#2C1810', border: '1px solid rgba(212, 165, 116, 0.2)' }}
                >
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base flex items-center justify-between" style={{ color: '#F5B941' }}>
                      <span>{getBlockDisplayName(filename)}</span>
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            className="text-[#D4A574] hover:text-[#F5B941] hover:bg-[#8B3A1F]/30"
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            View
                          </Button>
                        </DialogTrigger>
                        <DialogContent 
                          className="max-w-4xl max-h-[80vh] overflow-y-auto"
                          style={{ background: '#2C1810', border: '1px solid rgba(212, 165, 116, 0.3)' }}
                        >
                          <DialogHeader>
                            <DialogTitle style={{ color: '#F5B941' }}>{getBlockDisplayName(filename)}</DialogTitle>
                            <DialogDescription style={{ color: '#D4A574' }}>{filename}</DialogDescription>
                          </DialogHeader>
                          <div className="prose prose-invert prose-sm max-w-none" style={{ color: '#FFF8F0' }}>
                            <ReactMarkdown>{content}</ReactMarkdown>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p 
                      className="text-sm line-clamp-3"
                      style={{ color: '#D4A574' }}
                    >
                      {content.slice(0, 300)}...
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="transcript">
            <Card style={{ background: '#2C1810', border: '1px solid rgba(212, 165, 116, 0.2)' }}>
              <CardContent className="pt-6">
                {meeting.transcript ? (
                  <div className="prose prose-invert prose-sm max-w-none" style={{ color: '#FFF8F0' }}>
                    <pre className="whitespace-pre-wrap text-sm" style={{ color: '#D4A574' }}>
                      {meeting.transcript}
                    </pre>
                  </div>
                ) : (
                  <p style={{ color: '#D4A574' }}>No transcript available</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="manifest">
            <Card style={{ background: '#2C1810', border: '1px solid rgba(212, 165, 116, 0.2)' }}>
              <CardContent className="pt-6">
                <pre 
                  className="text-sm overflow-auto"
                  style={{ color: '#D4A574' }}
                >
                  {JSON.stringify(manifest, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Footer */}
        <footer className="mt-12 pt-6 text-center" style={{ borderTop: '1px solid rgba(212, 165, 116, 0.2)' }}>
          <p className="text-sm" style={{ color: '#D4A574', opacity: 0.7 }}>
            Powered by <span style={{ color: '#F5B941', fontWeight: 600 }}>N5 OS</span> • Built on Zo Computer
          </p>
        </footer>
      </main>
    </div>
  );
}

