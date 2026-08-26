import React, { useEffect, useState } from "react";
import DOMPurify from "dompurify";
import { marked } from "marked";

interface Artifact {
  id: string;
  title: string;
  content: string;
  artifact_type: string;
  created_at: string;
  updated_at: string;
}

interface ArtifactViewerProps {
  artifactId: string | null;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({
  artifactId,
}) => {
  const [html, setHtml] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!artifactId) {
      setHtml("");
      setError("");
      return;
    }

    const loadArtifact = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `http://localhost:8000/api/v1/artifacts/${artifactId}`
        );

        if (!response.ok) {
          throw new Error(`Failed to load artifact: ${response.status}`);
        }

        const data: Artifact = await response.json();

        const rawHtml = await marked.parse(data.content || "");

        const sanitizedHtml = DOMPurify.sanitize(rawHtml, {
          USE_PROFILES: {
            html: true,
          },
          FORBID_TAGS: [
            "script",
            "style",
            "iframe",
            "object",
            "embed",
            "form",
          ],
          FORBID_ATTR: [
            "onerror",
            "onload",
            "onclick",
            "onmouseover",
            "onfocus",
          ],
        });

        setHtml(sanitizedHtml);
      } catch (err) {
        console.error("Artifact loading error:", err);
        setError("Unable to load the artifact.");
      } finally {
        setLoading(false);
      }
    };

    loadArtifact();
  }, [artifactId]);

  if (!artifactId) {
    return (
      <div className="h-full flex items-center justify-center text-gray-400">
        No artifact selected
      </div>
    );
  }

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        Loading artifact...
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center text-red-500">
        {error}
      </div>
    );
  }

  return (
    <div className="h-full border rounded-lg bg-white flex flex-col overflow-hidden">
      <div className="px-4 py-3 bg-gray-100 border-b font-bold">
        Artifact Viewer
      </div>

      <div
        className="
          flex-1
          overflow-y-auto
          p-6
          prose
          prose-lg
          max-w-none
          text-gray-800
        "
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </div>
  );
};