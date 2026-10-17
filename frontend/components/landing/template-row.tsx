import { cn } from "cn"
import { useTranslations } from "next-intl"

import { Dotted } from "@/components/dot"

/** A template as a row of the templates list (components/templates/template-list.tsx), small:
 * its title and its topics and questions; tinted while `picked`. */
export function TemplateRow({
  ref,
  title,
  topics,
  questions,
  picked = false,
}: {
  ref?: React.Ref<HTMLLIElement>
  title: string
  topics: number
  questions: number
  picked?: boolean
}) {
  const t = useTranslations("templates")
  const practice = useTranslations("practice")

  return (
    <li
      ref={ref}
      className={cn(
        "space-y-0.5 px-3 py-2.5 transition-colors",
        picked && "bg-primary/5"
      )}
    >
      <span className="block font-medium">{title}</span>
      <span className="block text-xs text-muted-foreground">
        <Dotted
          items={[
            t("topics", { count: topics }),
            practice("questions", { count: questions }),
          ]}
        />
      </span>
    </li>
  )
}
