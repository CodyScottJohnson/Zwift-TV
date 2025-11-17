'use client'

import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"

export function QuickControls({children}: {children: React.ReactNode}) {
    return (
        <Sheet>
            <SheetTrigger asChild>
                {children}
            </SheetTrigger>
            <SheetContent className="bg-black-50 border-black-100">
                Quick Controls
            </SheetContent>
        </Sheet>
    )

}