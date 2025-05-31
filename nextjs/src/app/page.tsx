"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { IconButton } from "@/components/custom/IconButton";
import { Input } from "@/components/ui/Input";
import { Trash2, Edit, Save } from "lucide-react";

export default function DemoPage() {
  const [name, setName] = useState("");

  return (
    <div className="p-8 space-y-8">
      <h1 className="text-3xl font-bold">Component System Demo</h1>

      {/* Input Demo */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Inputs</h2>
        <div className="space-y-2">
          <Input
            placeholder="Default input"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Input
            placeholder="With outline tone"
            variantTone="outline"
            variantSize="md"
          />
          <Input
            placeholder="Ghost style"
            variantTone="ghost"
            variantSize="md"
          />
          <Input
            placeholder="Error input"
            variantIntent="error"
            variantTone="outline"
            variantSize="md"
          />
          <Input placeholder="Disabled input" disabled />
        </div>
      </section>

      {/* Button Demo */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Buttons</h2>
        <div className="flex flex-wrap gap-4">
          <Button>Default</Button>
          <Button variantIntent="secondary">Secondary</Button>
          <Button variantIntent="destructive">Destructive</Button>
          <Button variantTone="outline">Outline</Button>
          <Button variantTone="ghost">Ghost</Button>
          <Button disabled>Disabled</Button>
          <Button variantSize="sm">Small</Button>
          <Button variantSize="lg">Large</Button>
        </div>
      </section>

      {/* IconButton Demo */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Icon Buttons</h2>
        <div className="flex flex-wrap gap-4 items-center">
          <IconButton
            icon={<Trash2 size={16} />}
            variantIntent="destructive"
            variantShape="circle"
            variantEmphasis="strong"
            variantSize="sm"
            aria-label="Delete"
            title="Delete"
          />
          <IconButton
            icon={<Edit size={18} />}
            variantTone="outline"
            variantShape="square"
            variantEmphasis="subtle"
            variantSize="md"
            aria-label="Edit"
            title="Edit"
          />
          <IconButton
            icon={<Save size={20} />}
            variantIntent="primary"
            variantTone="solid"
            variantShape="circle"
            variantEmphasis="strong"
            variantSize="lg"
            aria-label="Save"
            title="Save"
          />
        </div>
      </section>
    </div>
  );
}
