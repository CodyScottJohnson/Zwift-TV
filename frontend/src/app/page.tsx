'use client'

import { ZwiftIcon, DisneyIcon, NetflixIcon } from "@/components/app";
import { QuickControls } from "@/components/layout/quick-controls";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-between py-32 px-16  sm:items-start">
        <h1 className="mb-8 text-4xl font-bold text-white">
          Hello Abby!
        </h1>
        <div className="flex items-center gap-6">
          <NetflixIcon />
          <DisneyIcon />
          <ZwiftIcon />
        </div>

        <QuickControls>
          <Button>Open Quick Controls</Button>
        </QuickControls>

      </main>
    </div>
  );
}
