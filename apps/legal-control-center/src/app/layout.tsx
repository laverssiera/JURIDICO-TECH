import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Providers from "./providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "Jurídico.Tech — Legal Command Center",
  description: "Infraestrutura Cognitiva Regulatória — LICEU 6.x",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={`${inter.variable} h-full`}>
      <body className="h-full bg-[#080b12] text-slate-200 antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
