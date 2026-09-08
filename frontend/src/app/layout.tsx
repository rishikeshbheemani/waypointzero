import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WaypointZero | Autonomous Travel System",
  description: "Autonomous multi-agent travel planning and refinement engine powered by LangGraph.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-black text-white antialiased selection:bg-white selection:text-black">
        {children}
      </body>
    </html>
  );
}
