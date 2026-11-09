import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CashOrbit | B2B Receivables & Working Capital",
  description:
    "Portfolio fintech platform for invoicing, payments, bank reconciliation, collections, and AI-assisted finance operations.",
  keywords: [
    "fintech",
    "accounts receivable",
    "working capital",
    "reconciliation",
    "B2B",
    "portfolio project",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
