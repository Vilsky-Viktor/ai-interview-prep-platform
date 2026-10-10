"use client"

import { useTranslations } from "next-intl"

import { Chips } from "@/components/company/ats-steps"
import { CopyValue } from "@/components/copy-field"
import { InstructionsDialog } from "@/components/instructions-dialog"
import {
  CHATGPT_AUTH,
  CHATGPT_CREATE,
  CHATGPT_DEVELOPER_PATH,
  CLAUDE_CONNECTOR_PATH,
  MCP_NAME,
  MCP_PATH,
} from "@/constants/ai-apps"
import { useOrigin } from "@/lib/origin"

/** The MCP server's Instructions button, on its row and its page, like the other integrations':
 * a dialog with the server's address to copy, then Claude's steps (and Claude Code's one
 * command) and ChatGPT's, in the ATS steps' style. */
export function AiAppsInstructions() {
  const t = useTranslations("aiApps")
  const ats = useTranslations("ats")
  const origin = useOrigin()
  const url = origin ? `${origin}${MCP_PATH}` : ""
  const command = url
    ? `claude mcp add --transport http ${MCP_NAME} ${url}`
    : ""

  return (
    <InstructionsDialog title={t("instructionsTitle")}>
      <Section title={t("serverTitle")} text={t("serverText")}>
        <CopyValue value={url} label={ats("copyUrl")} copied={ats("copied")} />
      </Section>
      <Section title={t.rich("addTo", { name: "Claude", app: KeepCase })}>
        <ol className="list-decimal space-y-3 ps-5 text-base text-muted-foreground">
          <li className="space-y-1.5">
            <span className="block">{t("claudeOpen")}</span>
            <Chips items={CLAUDE_CONNECTOR_PATH} path />
          </li>
          <li>{t("claudePaste", { name: MCP_NAME })}</li>
          <li>{t("allowOnPrepza")}</li>
        </ol>
        <div className="space-y-2">
          <p className="text-base text-muted-foreground">{t("claudeCode")}</p>
          <CopyValue
            value={command}
            label={t("copyCommand")}
            copied={t("commandCopied")}
          />
        </div>
      </Section>
      <Section title={t.rich("addTo", { name: "ChatGPT", app: KeepCase })}>
        <ol className="list-decimal space-y-3 ps-5 text-base text-muted-foreground">
          <li className="space-y-1.5">
            <span className="block">{t("chatgptDeveloper")}</span>
            <Chips items={CHATGPT_DEVELOPER_PATH} path />
          </li>
          <li className="space-y-1.5">
            <span className="block">{t("chatgptCreate")}</span>
            <Chips items={[CHATGPT_CREATE]} />
          </li>
          <li className="space-y-1.5">
            <span className="block">
              {t("chatgptPaste", { name: MCP_NAME })}
            </span>
            <Chips items={[CHATGPT_AUTH]} />
          </li>
          <li>{t("allowOnPrepza")}</li>
        </ol>
      </Section>
    </InstructionsDialog>
  )
}

/** A part of the instructions: its title, what it's for when there's more to say, then its
 * content. */
function Section({
  title,
  text,
  children,
}: {
  title: React.ReactNode
  text?: string
  children: React.ReactNode
}) {
  return (
    <section className="space-y-4">
      <div className="space-y-1">
        <h3 className="text-lg font-medium">{title}</h3>
        {text && <p className="text-base text-muted-foreground">{text}</p>}
      </div>
      {children}
    </section>
  )
}

/** An app's name in a lowercase title, keeping its own capitals. */
function KeepCase(chunks: React.ReactNode) {
  return <span className="normal-case">{chunks}</span>
}
