# Data protection impact assessment (DPIA): template for companies using prepza

Version: 2026-10-06\
Operator: Arcolabs OÜ (registry code 17587452), Sepapaja tn 6, 15551 Tallinn, Harju maakond, Estonia; hello@prepza.ai

For companies that invite candidates through prepza. Your company is the **controller** of
candidates' interview data; Arcolabs OÜ (prepza) is your **processor**. Parts marked
**[COMPANY]** are yours to complete. Parts already filled describe prepza as of the version date;
the current data processing agreement (prepza.ai/dpa) and privacy policy (prepza.ai/privacy) take
precedence. This is a template, not legal advice.

Whether you need a DPIA is your decision. Many EU supervisory authorities list systematic
evaluation of candidates, new technologies and AI in recruitment among the cases that require one;
check your authority's list.

## 1. Overview

| Item | Answer |
|---|---|
| Controller | **[COMPANY]** name, address, DPO or privacy contact |
| Processor | Arcolabs OÜ, registry code 17587452, Sepapaja tn 6, 15551 Tallinn, Harju maakond, Estonia; hello@prepza.ai |
| Roles / vacancies covered | **[COMPANY]** |
| Countries of candidates | **[COMPANY]** |
| Assessment owner and date | **[COMPANY]** |

## 2. Description of the processing

**Purpose.** Assessing job knowledge of candidates for **[COMPANY: role]** with a timed
multiple-choice test, as one input to a hiring decision made by **[COMPANY: who]**.

**How it works.**

1. You paste a job description; AI (OpenAI models) proposes topics; you review and edit them.
2. AI writes a bank of multiple-choice questions per topic; you can try the interview as a
   candidate and report any question whose answer looks wrong.
3. You invite candidates by email (or share a link). Each invited candidate signs in (Google,
   LinkedIn or GitHub) with the invited email address, and gets a random subset of questions with a
   timer on each.
4. prepza marks each answer right or wrong against the question's answer key and shows you a
   percentage grade, green or red against the passing grade you set, ranked best first, with
   integrity signals.
5. You review results and decide. prepza sends candidates no decision.

**Data categories.**

| Category | Details |
|---|---|
| Identity and contact | Invited email address; name and account id from sign-in |
| Assessment | Questions shown, answers, right/wrong, time per answer, timeouts, topic and overall grades, pass/fail against your passing grade, rank |
| Accommodations | Extra time you give a candidate (the amount only, never a reason) |
| Integrity signals | Times the candidate left the page, copy attempts, answers under 3 seconds, each with the question on screen |
| Feedback | Candidate's ratings and reports of questions (reports may include a free-text comment) |
| Reports | PDFs made in your browser; if emailed through prepza, kept at most 7 days to send |
| Special categories | None requested. **[COMPANY]** confirm you do not add any (e.g. in job descriptions or notes) |

**Data subjects.** Job candidates **[COMPANY: approx. number per year]**; your staff using prepza.

**Recipients and sub-processors** (per prepza's privacy policy and DPA at prepza.ai/dpa):

- Google Cloud (hosting, database, events, in the EU region europe-west1) and Google Firebase
  (sign-in).
- OpenAI (writing and checking questions; receives job descriptions, questions, how many people
  picked each option, and the reasons questions were reported, never reporters' comments,
  candidates' emails or individual answers).
- Resend (emails).
- Sentry (error reports, without email addresses).
- Upstash (short-lived counters for limits and live updates).
- Paddle (payments; receives no candidate data).

**International transfers.** Some sub-processors are in the US. Transfers outside the EU are
covered by the EU-US Data Privacy Framework or the European Commission's standard contractual
clauses (see the DPA).

**Retention.** Candidate results, timings and signals: deleted automatically 12 months after the
invite was last sent. Unstarted invites expire after 30 days. Job description text in generation
records: 90 days. Database backups: 14 days, then overwritten. **[COMPANY]**: your own retention of
downloaded PDFs and notes.

**Automated decision-making.** prepza computes a grade and ranking but makes no decision. Whether
your process is "solely automated" under GDPR Art. 22 depends on how you use it. **[COMPANY]**
describe who reviews results and how (see section 5).

## 3. Necessity and proportionality

| Question | Answer |
|---|---|
| Lawful basis | **[COMPANY]** usually legitimate interest (Art. 6(1)(f)) or steps before a contract (Art. 6(1)(b)); record your balancing test |
| Is the knowledge tested a genuine requirement of the role? | **[COMPANY]** you approved the topics; keep that record |
| Could a less intrusive method work? | **[COMPANY]** |
| Data minimisation | Only sign-in details and test data; no CV, video, voice or demographics are collected by prepza |
| Information to candidates | Invite page tells candidates what to expect, that leaving the page and copying are recorded, that questions are AI-written, that people at your company decide and can review their result, and to ask you for more time if needed. **[COMPANY]** add your notice (see prepza's candidate notice templates) |
| Rights | Access: candidate's scorecard page and PDF report give you everything to answer; erasure: "Delete candidate" on the candidate's page; objection: **[COMPANY]** process; candidates can also write to prepza, who passes requests on |
| Human review on request | **[COMPANY]** who handles it and how fast |
| Accommodations | Extra time per candidate (+25%, +50% or +100%), set before they start, no reason stored; **[COMPANY]** alternative process |

## 4. Risks to candidates

Likelihood and severity: **[COMPANY]** to rate. Starting points from prepza:

| Risk | Typical source | prepza controls | Your controls **[COMPANY]** |
|---|---|---|---|
| Unfair rejection from a wrong or ambiguous question | AI-written content | Your topic review and trial run; answer keys checked before release; statistics and reports flag questions for a fix, and corrected keys re-mark past answers | |
| Discrimination (age, disability, language, origin) | Time pressure, language, content | Knowledge questions only; questions flagged when too slow or not discriminating; extra time | |
| Over-reliance on the grade or signals | Ranked list, green/red | All answers visible; signals as counts; no automatic decisions | |
| Wrongful cheating suspicion | Page-leave and fast-answer signals | Shown as hints with the question on screen | |
| Lack of transparency | Candidates don't see their grade | Privacy policy; invite page notice | |
| Data breach | Hosting, sub-processors | Access controls, encryption by Google Cloud, error reports without emails, retention limits | |
| Excessive retention | | Automatic deletion after 12 months | |

## 5. Measures to reduce risk **[COMPANY]**

- [ ] Topics reviewed against the job's real requirements and the review recorded
- [ ] Interview tried by someone who knows the role before inviting
- [ ] Passing grade chosen and justified (not just the default 70%)
- [ ] A named person reviews every candidate's scorecard before a rejection
- [ ] Integrity signals never the sole reason to reject
- [ ] Candidate notice sent before the invite; accommodation route offered
- [ ] Human review offered on request, with a response time
- [ ] Adverse impact checked on your own hiring outcomes where lawful
- [ ] Downloaded PDFs kept no longer than your retention period
- [ ] New York City roles: see prepza's instructions for companies

## 6. Sign-off **[COMPANY]**

| | Name | Date | Notes |
|---|---|---|---|
| Measures approved by | | | |
| Residual risks accepted by | | | |
| DPO advice | | | |
| Review date | | | |
