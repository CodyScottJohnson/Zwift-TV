import { cn } from "@/lib/utils"

export function BaseIcon({children,className}: {children: React.ReactNode,className?: string}) {
    return (
        <div className={cn("h-32 aspect-square inline-flex p-4 items-center justify-center bg-black-50 rounded-lg shadow-ios-card",
            className)}>
                {children}

        </div>
    )
}