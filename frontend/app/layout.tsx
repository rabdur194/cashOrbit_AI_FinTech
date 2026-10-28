import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "CashOrbit | Finance Operations", description: "B2B receivables and financial operations platform" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
