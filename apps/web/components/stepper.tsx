"use client";

import { CheckCircle2 } from "lucide-react";

export type Step = {
  title: string;
  description?: string;
};

export default function Stepper({ steps }: { steps: Step[] }) {
  return (
    <ol className="space-y-3">
      {steps.map((s, idx) => (
        <li key={idx} className="flex gap-3">
          <div className="mt-0.5">
            <CheckCircle2 className="h-5 w-5 text-muted-foreground" />
          </div>
          <div>
            <div className="text-sm font-medium">
              {idx + 1}. {s.title}
            </div>
            {s.description && (
              <div className="text-xs text-muted-foreground">{s.description}</div>
            )}
          </div>
        </li>
      ))}
    </ol>
  );
}
