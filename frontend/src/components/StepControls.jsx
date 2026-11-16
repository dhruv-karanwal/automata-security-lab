import React, { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Play, Pause, RotateCcw } from "lucide-react";
import { moveCursor } from "../utils/traceModel.js";
function usePlayback(length) {
  const [index, setIndex] = useState(0), [playing, setPlaying] = useState(false);
  const last = Math.max(0, length - 1);
  useEffect(() => {
    setIndex(0);
    setPlaying(false);
  }, [length]);
  useEffect(() => {
    if (!playing) return;
    if (index >= last) {
      setPlaying(false);
      return;
    }
    const id = setTimeout(() => setIndex((i) => Math.min(last, i + 1)), 900);
    return () => clearTimeout(id);
  }, [playing, index, last]);
  return { index, playing, setPlaying, setIndex, last, reset: () => {
    setPlaying(false);
    setIndex(0);
  } };
}
function StepControls({ playback, label = "Execution step" }) {
  const { index, last, playing, setPlaying, setIndex } = playback;
  function move(action) {
    setPlaying(false);
    setIndex((i) => moveCursor(i, action, last));
  }
  return <div className="controls" role="group" aria-label={label}><button className="btn compact" disabled={index === 0} onClick={() => move("back")}><ChevronLeft size={14} />Back</button><button className="btn compact" disabled={last === 0 || index === last} onClick={() => setPlaying(!playing)}>{playing ? <Pause size={14} /> : <Play size={14} />} {playing ? "Pause" : "Play"}</button><button className="btn compact" disabled={index === last} onClick={() => move("next")}>Next<ChevronRight size={14} /></button><button className="btn compact" onClick={() => move("reset")}><RotateCcw size={13} />Reset</button><input aria-label={label} type="range" min="0" max={last} value={index} onChange={(e) => {
    setPlaying(false);
    setIndex(Number(e.target.value));
  }} /><span className="tiny mono" aria-live="polite">{index} / {last}</span></div>;
}
export {
  StepControls as default,
  usePlayback
};
