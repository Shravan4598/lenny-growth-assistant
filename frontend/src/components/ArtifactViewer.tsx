import React, { useEffect, useState } from 'react';
import DOMPurify from 'dompurify';
import { marked } from 'marked';

export const ArtifactViewer: React.FC<{ artifactId: string | null }> = ({ artifactId }) => {
  const [html, setHtml] = useState<string>("");

  useEffect(() => {
    if (!artifactId) return;
    
    fetch(`http://localhost:8000/api/v1/artifacts/${artifactId}`)
      .then(res => res.json())
      .then(async data => {
        // Parse markdown to HTML
        const rawHtml = await marked.parse(data.content);
        
        // Sanitize aggressively to prevent XSS
        const sanitized = DOMPurify.sanitize(rawHtml, {
          USE_PROFILES: { html: true },
          FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed'],
          FORBID_ATTR: ['onerror', 'onload', 'onclick']
        });
        
        const wrapped = `<html><head><style>body{font-family:sans-serif;padding:20px;line-height:1.6;}</style></head><body>${sanitized}</body></html>`;
        setHtml(wrapped);
      });
  }, [artifactId]);

  if (!artifactId) return <div className="p-10 text-gray-400 text-center border h-full">No artifact selected</div>;

  return (
    <div className="h-full border rounded shadow bg-white flex flex-col">
      <div className="p-3 bg-gray-100 border-b font-bold">Artifact Viewer</div>
      {/* Sandbox completely disables JS execution in the generated content */}
      <iframe sandbox="allow-same-origin" srcDoc={html} className="w-full h-full border-none" />
    </div>
  );
};