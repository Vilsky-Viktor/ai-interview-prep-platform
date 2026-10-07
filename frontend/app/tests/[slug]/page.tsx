import Link from "next/link"
import { notFound, permanentRedirect } from "next/navigation"
import { getTranslations } from "next-intl/server"

import { BackLink } from "@/components/back-link"
import { JsonLd } from "@/components/json-ld"
import { PageHeader } from "@/components/page-header"
import { SubtopicList } from "@/components/questions/subtopic-list"
import { SampleQuestions } from "@/components/tests/sample-questions"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { serverFetch } from "@/lib/server-api"
import { pageMetadata, siteUrl } from "@/lib/site"
import { breadcrumbData } from "@/lib/structured-data"
import type { SampleQuestion, Template } from "@/types/superadmin"

type Params = { params: Promise<{ slug: string }> }

export async function generateMetadata({ params }: Params) {
  const { slug } = await params
  const t = await getTranslations("tests")
  const template = await serverFetch<Template>(`/library/templates/${slug}`)

  return template
    ? pageMetadata(
        t("pageTitle", { role: template.title }),
        t("pageDescription", {
          role: template.title,
          count: template.topic_count,
        }),
        `/tests/${template.slug ?? template.id}`
      )
    : {}
}

/** A role's skills test for companies hiring for it, made from its template: what it checks,
 * the way to test candidates, and sample questions (which also answer candidates' searches,
 * with a link to free practice). Its address is the template's slug. */
export default async function RoleTestPage({ params }: Params) {
  const { slug: key } = await params
  const t = await getTranslations("tests")
  const template = await serverFetch<Template>(`/library/templates/${key}`)

  if (!template) {
    notFound()
  }

  if (template.slug && key !== template.slug) {
    permanentRedirect(`/tests/${template.slug}`)
  }

  const slug = template.slug ?? template.id
  const questions =
    (await serverFetch<SampleQuestion[]>(
      `/library/templates/${slug}/sample`
    )) ?? []

  return (
    <main className="mx-auto max-w-5xl space-y-10 px-6 py-12">
      <JsonLd
        data={breadcrumbData(siteUrl(), [
          { name: "prepza", path: "/" },
          { name: t("title"), path: "/tests" },
          { name: template.title, path: `/tests/${slug}` },
        ])}
      />
      <PageHeader
        back={<BackLink href="/tests">{t("title")}</BackLink>}
        tags={
          <>
            <Badge variant="outline" className="h-7 px-3 text-sm font-light">
              {template.level}
            </Badge>
            <Badge
              variant="outline"
              className="h-7 px-3 text-sm font-light uppercase"
            >
              {template.language}
            </Badge>
          </>
        }
        title={
          <h1 className="font-heading text-3xl font-medium tracking-tight text-balance normal-case">
            {t("heading", { role: template.title })}
          </h1>
        }
      />
      <div className="space-y-6">
        <p className="text-lg text-muted-foreground">{t("lead")}</p>
        <div className="flex flex-wrap items-center gap-3">
          <Button
            className="h-12 px-6 text-base"
            render={<Link href="/" />}
            nativeButton={false}
          >
            {t("create")}
          </Button>
          <Button
            variant="outline"
            className="h-12 px-6 text-base"
            render={<Link href={`/practice/${slug}`} />}
            nativeButton={false}
          >
            {t("practise")}
          </Button>
        </div>
      </div>

      <section className="space-y-4">
        <h2 className="font-heading text-2xl font-medium">{t("topics")}</h2>
        <ul lang={template.language} className="divide-y rounded-2xl border">
          {template.topics.map((topic) => (
            <li key={topic.id} className="space-y-3 p-4 sm:p-6">
              <span className="block text-lg font-medium">{topic.title}</span>
              <SubtopicList subtopics={topic.subtopics} />
            </li>
          ))}
        </ul>
      </section>

      {questions.length > 0 && (
        <SampleQuestions questions={questions} language={template.language} />
      )}
    </main>
  )
}
