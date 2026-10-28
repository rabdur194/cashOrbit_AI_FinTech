import type { ReactNode } from "react";
import type { Page } from "../lib/types";
export function Heading({
  eyebrow,
  title,
  subtitle,
  action,
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      {action}
    </div>
  );
}
export function Metric({
  label,
  value,
  foot,
  icon: Icon,
  accent = false,
}: {
  label: string;
  value: string;
  foot: string;
  icon: any;
  accent?: boolean;
}) {
  return (
    <div className="metric">
      <div className="metric-top">
        <span>{label}</span>
        <div
          className="metric-icon"
          style={accent ? { background: "#fff1e5", color: "#c77b20" } : {}}
        >
          <Icon size={17} />
        </div>
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-foot">{foot}</div>
    </div>
  );
}
export function Status({ value }: { value: string }) {
  return (
    <span className={`status ${value}`}>{value.replaceAll("_", " ")}</span>
  );
}
export function initials(s: string) {
  return s
    .split(/\s+/)
    .map((x) => x[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}
