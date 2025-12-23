"use client";

import { useState, useEffect } from 'react';

// --- Types ---
interface Ability {
  id?: number;
  template_name: string;
  friendly_name: string;
  description: string;
  help_text: string;
  promotion_text: string;
  flyover_text: string;
  source_file: string;
}

interface ScanResult {
  status: string;
  count: number;
}

export default function Home() {
  // State
  const [modPath, setModPath] = useState<string>("C:\\Program Files (x86)\\Steam\\steamapps\\workshop\\content\\268500");
  const [abilities, setAbilities] = useState<Ability[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string>("");

  // Load on mount
  useEffect(() => {
    fetchAbilities();
  }, []);

  // Fetch from Python Backend
  const fetchAbilities = async () => {
    try {
      // NOTE: Ensure port matches your backend (8000 or 8001)
      const response = await fetch("http://localhost:8003/abilities");
      const data: Ability[] = await response.json();
      setAbilities(data);
    } catch (error) {
      console.error("Failed to fetch abilities:", error);
    }
  };

  // Trigger Scan
  const handleScan = async () => {
    setIsLoading(true);
    setStatusMessage("Scanning... this might take a moment.");
    
    try {
      const encodedPath = encodeURIComponent(modPath);
      const response = await fetch(`http://localhost:8003/scan?path=${encodedPath}`);
      const result: ScanResult = await response.json();
      
      if (result.status === "success") {
        setStatusMessage(`Scan complete! Found ${result.count} abilities.`);
        fetchAbilities(); 
      } else {
        setStatusMessage("Scan failed.");
      }
    } catch (error) {
      setStatusMessage("Error connecting to backend.");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  // Filter Logic
  const filteredAbilities = abilities.filter(ability => 
    (ability.friendly_name || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
    (ability.template_name || "").toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <main className="min-h-screen bg-zinc-900 text-zinc-100 p-8 font-sans">
      <div className="max-w-7xl mx-auto">
        
        {/* --- Header --- */}
        <header className="mb-8 border-b-2 border-cyan-800 pb-4 flex justify-between items-end">
          <h1 className="text-4xl font-bold text-cyan-400 tracking-wider uppercase">
            XCOM 2 Ability Architect
          </h1>
          <div className="text-zinc-500 text-sm font-mono">
            {filteredAbilities.length} Abilities Loaded
          </div>
        </header>

        {/* --- Control Panel --- */}
        <section className="bg-zinc-800 p-6 rounded-lg shadow-lg border border-zinc-700 mb-8">
          <div className="flex flex-col md:flex-row gap-4 items-end">
            <div className="flex-grow w-full">
              <label className="block text-sm font-semibold text-zinc-400 mb-2">
                Mod Directory Path
              </label>
              <input 
                type="text" 
                value={modPath} 
                onChange={(e) => setModPath(e.target.value)} 
                className="w-full bg-zinc-950 border border-zinc-600 focus:border-cyan-500 rounded p-3 text-white outline-none transition-colors"
                placeholder="Paste your Workshop path here..."
              />
            </div>
            <button 
              onClick={handleScan} 
              disabled={isLoading}
              className={`
                px-6 py-3 rounded font-bold uppercase tracking-wide transition-all min-w-[150px]
                ${isLoading 
                  ? "bg-zinc-600 text-zinc-400 cursor-not-allowed" 
                  : "bg-cyan-700 hover:bg-cyan-600 text-white shadow-lg shadow-cyan-900/50"}
              `}
            >
              {isLoading ? "Scanning..." : "Scan Mods"}
            </button>
          </div>
          {statusMessage && (
            <div className="mt-4 text-sm text-cyan-300 font-mono">
              &gt; {statusMessage}
            </div>
          )}
        </section>

        {/* --- Library Section --- */}
        <section>
          <div className="mb-6">
            <input 
              type="text" 
              placeholder="Search abilities (e.g., 'Unbalance' or 'Shot')..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-zinc-950 border border-zinc-700 focus:border-cyan-500 rounded p-3 text-white outline-none"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredAbilities.map((ability, index) => (
              <div 
                key={ability.id || index} 
                className="bg-zinc-800/50 border border-zinc-700 p-5 rounded hover:border-cyan-500/50 hover:bg-zinc-800 transition-all flex flex-col relative"
              >
                <div className="mb-3 relative group">
                  {/* HOVER TRIGGER: The Title */}
                  <h3 className="text-xl font-bold text-cyan-400 cursor-help underline decoration-dotted decoration-cyan-700 underline-offset-4">
                    {ability.friendly_name || "Unknown Ability"}
                  </h3>
                  
                  {/* TOOLTIP: Hidden by default, shown on group-hover */}
                  <div className="absolute opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto z-50 bottom-full left-0 w-[400px] mb-2 p-4 bg-zinc-950 border border-cyan-500 shadow-2xl rounded text-sm transition-opacity duration-200">
                    <h4 className="text-cyan-400 font-bold mb-2 border-b border-zinc-700 pb-1">Raw Data Preview</h4>
                    
                    <div className="space-y-2">
                      <div>
                        <span className="text-zinc-500 block text-xs uppercase">Template Name:</span>
                        <code className="text-white bg-zinc-900 px-1 rounded">{ability.template_name}</code>
                      </div>
                      
                      {ability.promotion_text && (
                        <div>
                          <span className="text-zinc-500 block text-xs uppercase">Promotion Text:</span>
                          <p className="text-zinc-300">{ability.promotion_text.replace(/<[^>]+>/g, '')}</p>
                        </div>
                      )}

                      {ability.flyover_text && (
                        <div>
                          <span className="text-zinc-500 block text-xs uppercase">Flyover Text:</span>
                          <p className="text-zinc-300 italic">"{ability.flyover_text}"</p>
                        </div>
                      )}

                      {ability.help_text && (
                        <div>
                          <span className="text-zinc-500 block text-xs uppercase">Help Text:</span>
                          <p className="text-zinc-300">{ability.help_text}</p>
                        </div>
                      )}
                    </div>
                    
                    {/* Tiny arrow pointing down */}
                    <div className="absolute top-full left-4 w-0 h-0 border-l-8 border-l-transparent border-r-8 border-r-transparent border-t-8 border-t-cyan-500"></div>
                  </div>

                  <code className="text-xs text-zinc-500 font-mono block mt-1">
                    {ability.template_name}
                  </code>
                </div>
                
                <p className="text-zinc-300 text-sm leading-relaxed flex-grow line-clamp-4">
                  {ability.description 
                    ? ability.description.replace(/<[^>]+>/g, '') // Strip HTML
                    : <span className="text-zinc-600 italic">No description provided.</span>}
                </p>

                <div className="mt-4 pt-4 border-t border-zinc-700/50 text-xs text-zinc-500 truncate text-right font-mono" title={ability.source_file}>
                   ...{ability.source_file ? ability.source_file.split('\\').slice(-3).join('\\') : "unknown"}
                </div>
              </div>
            ))}
          </div>
        </section>

      </div>
    </main>
  );
}