import { Orbit } from "lucide-react";

export default function Logo() {
  return (
    <div className="brand-mark">
      <span className="brand-icon" aria-hidden="true"><Orbit size={20} strokeWidth={1.8} /></span>
      <span>Invest<span className="brand-accent">Twin</span></span>
    </div>
  );
}