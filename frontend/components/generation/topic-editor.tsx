"use client"

import { PlusIcon, XIcon } from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type { DraftTopic } from "@/types/generation"

type TopicEditorProps = {
  topic: DraftTopic
  onChange: (topic: DraftTopic) => void
  onDone: () => void
}

/** Rename a topic and change its subtopics by hand, without asking the model. */
export function TopicEditor({ topic, onChange, onDone }: TopicEditorProps) {
  const [newSubtopic, setNewSubtopic] = useState("")
  const name = topic.main_topic.trim()

  function addSubtopic() {
    const subtopic = newSubtopic.trim()

    if (subtopic && !topic.subtopics.includes(subtopic)) {
      onChange({ ...topic, subtopics: [...topic.subtopics, subtopic] })
    }

    setNewSubtopic("")
  }

  function removeSubtopic(index: number) {
    onChange({
      ...topic,
      subtopics: topic.subtopics.filter((_, item) => item !== index),
    })
  }

  return (
    <div className="space-y-4 p-6">
      <Input
        value={topic.main_topic}
        onChange={(event) =>
          onChange({ ...topic, main_topic: event.target.value })
        }
        aria-label="Topic name"
        aria-invalid={!name}
        className="h-10 font-medium"
        autoFocus
      />

      <ul className="flex flex-wrap gap-2">
        {topic.subtopics.map((subtopic, index) => (
          <li
            key={subtopic}
            className="flex items-center gap-1 rounded-full bg-muted py-1 pr-1 pl-3 text-sm"
          >
            {subtopic}
            <Button
              type="button"
              variant="ghost"
              size="icon-xs"
              className="rounded-full"
              aria-label={`Remove ${subtopic}`}
              onClick={() => removeSubtopic(index)}
            >
              <XIcon />
            </Button>
          </li>
        ))}
      </ul>

      <div className="flex items-center gap-2">
        <Input
          value={newSubtopic}
          onChange={(event) => setNewSubtopic(event.target.value)}
          onKeyDown={(event) => {
            // Enter adds the subtopic instead of submitting the review.
            if (event.key === "Enter") {
              event.preventDefault()
              addSubtopic()
            }
          }}
          placeholder="Add a subtopic"
          aria-label="New subtopic"
          className="h-10"
        />
        <Button
          type="button"
          variant="outline"
          className="h-10 px-3"
          disabled={!newSubtopic.trim()}
          onClick={addSubtopic}
        >
          <PlusIcon />
          Add
        </Button>
        <Button
          type="button"
          variant="secondary"
          className="h-10 px-4"
          disabled={!name}
          onClick={onDone}
        >
          Done
        </Button>
      </div>
    </div>
  )
}
