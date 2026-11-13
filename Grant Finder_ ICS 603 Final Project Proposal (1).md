# Grant Finder: ICS 603 Final Project Proposal

*October 20, 2026*

## Project Goal

A grant finder and tracker that helps staff at small Hawaii nonprofits find grants they are eligible for, see why each one fits, and track their applications in one place.

## Intended User and Problem

The intended user is a program or development staff member at a small Hawaii nonprofit (under about 10 staff) working in education, culture, food, or the environment. Grant-seeking is usually one part of that person's job, not their whole job.

### What is hard today

- Grant listings are spread across foundation websites, county pages, PDFs, and Grants.gov, with no single place to check.
- Eligibility rules are written in long, vague prose, so deciding whether the organization qualifies means reading every listing in full.
- Deadlines and application status are tracked in personal spreadsheets or email, so opportunities are missed.

To confirm this problem, I will interview one nonprofit staff member about how they search for grants today (see the section on Next Investigation).

---

## Example Input

An organization description the user types in plain language (synthetic):

> "We're a 501(c)(3) on O'ahu with 4 staff. We run after-school coding and Hawaiian culture programs for about 60 middle schoolers in Waianae. Annual budget is around $350k. We want money for laptops and a summer program next year."

The app turns this into structured fields:

- Organization type: 501(c)(3)
- Island: O'ahu
- Focus areas: youth education, STEM, Hawaiian culture
- Population served: middle school students
- Budget: about $350k
- Needs: equipment, summer programming

---

## Sample Input Set

The organization profiles below are synthetic. The grant listings they are matched against are real public listings (see Data Source). The inputs will live in a `samples/` folder in the project repo, with one file per profile and its expected matches.

| # | Input (org profile, summarized) | Expected result |
|---|---|---|
| 1 | O'ahu 501(c)(3), youth coding + Hawaiian culture, $350k budget | Youth education and STEM grants ranked first; grants restricted to other islands are excluded |
| 2 | Hawai'i Island food bank, $1.2M budget | Food security grants matched; youth-only grants ranked low |
| 3 | Maui wildfire recovery group, fiscally sponsored (not a 501(c)(3)) | Grants that require 501(c)(3) status excluded, with the reason shown |
| 4 | Kaua'i watershed restoration nonprofit | Environmental and conservation grants matched |
| 5 | Hawaiian language immersion school support group | Culture, language, and education grants matched |
| 6 | Profile with no island or location given | App asks for the location before matching (no guess) |
| 7 | Profile whose only good match has a deadline that already passed | That grant not shown as a match; listed under "Closed" instead |
| 8 | Very short profile: "we help kupuna" | App asks follow-up questions (org type, island, budget) before matching |

I will check that the synthetic profiles are realistic by comparing them against public "About us" pages of real Hawaii nonprofits and by asking my interviewee whether they read like real organizations.

---

## Expected Result and Value

Afterward, the user sees a ranked list of grants they likely qualify for. Each grant shows the amount, the deadline, a one-line reason it fits, and the exact eligibility sentence the reason is based on. They can save a grant to their tracker and update its status as they apply.

A strong sign that the app helps would be this comparison: give a nonprofit staff member the same profile and 30 grant listings, then compare (a) the time it takes to build a shortlist by hand with (b) the time using the app, and the number of eligible grants that each approach misses. A shorter time with no more missed grants would indicate clear improvement.

---

## Big-Picture Sketch

The user starts in Area 1, confirms the extracted fields in Area 2, reviews matches in Area 3 (the main result), and saves them to the tracker in Area 4. Area 4 is also how they return to saved work. Each area becomes a main block of the app. Grant names are placeholders.

```text
Org description -> Confirmed profile -> Match results -> Saved tracker
       ^                                     |
       |                                     v
     user input                        application status
```

---

## Workflow Sketch

The path snakes from the organization description (top left) to the database (bottom left). First, a semantic search over grant descriptions identifies the most relevant candidates for the organization profile. Then hard eligibility rules are checked in code, and the LLM only scores the remaining shortlist and explains fit. When scoring fails, grants go to a Needs Review list instead of being dropped.

This approach supports future growth: for a larger dataset such as Grants.gov listings, the app can retrieve the top matches by meaning before running per-grant scoring, which reduces unnecessary LLM calls and makes the system more scalable.

---

## Data Source and Access

- Grant listings (real, public): 20–40 grants hand-collected into a spreadsheet containing name, funder, link, full description text, amount, deadline, and retrieved-on date.
- Sources: Hawaii-focused foundation pages (for example, Hawaii Community Foundation), county and state grant pages, and a few listings from Grants.gov.
- Optional later: the Grants.gov public search API, to pull federal listings automatically.
- Organization profiles (synthetic): written by me and labeled as synthetic.
- Listing freshness: each grant record will store a `retrieved_on` date and display it alongside the deadline so the user knows when the source was last checked.

Sensitivity is low. Grant listings are public, and profiles are synthetic. I will not use any real organization's financials, donor names, or staff details.

---

## Core Features

1. Org profile from plain language: the user describes their organization, the LLM extracts structured fields, and the user confirms or corrects them.
2. Grant matching with reasons: the app filters grants by hard rules (deadline, location, 501(c)(3) status), then the LLM ranks the rest and explains each fit by quoting the eligibility text it used.
3. Application tracker: the user saves grants and moves each through Interested, Applying, Submitted, Awarded, or Declined, with notes.

---

## LLM Role

The model does three jobs: it extracts profile fields, extracts grant rules, and classifies fit with a short drafted reason.

| Task | Input fields | Output fields |
|---|---|---|
| Profile extraction | free-text org description | org_type, island, focus_areas[], population_served, budget_usd, funding_needs[], missing_fields[] |
| Grant rule extraction (once per listing) | grant description text | eligible_org_types[], islands[], focus_areas[], min/max amount, deadline, requires_501c3, eligibility_quote |
| Fit classification | confirmed profile + one grant's extracted rules and text | fit (strong / possible / no), reason (one sentence), quoted_text, needs_review (true / false) |

Hard rules such as deadlines and 501(c)(3) status are checked in code, not by the model.

---

## Data Use

For each match run, the app looks up every grant listing and compares it with the confirmed organization profile on deadline, location, organization type, focus area, and amount range. It also looks up the user's existing tracker entries so it does not re-suggest grants already saved or declined.

---

## Saved Records

| Record | Created when | Links to |
|---|---|---|
| Organization profile | User confirms extracted fields | Match runs, applications |
| Grant | Listing imported from the spreadsheet | Matches, applications |
| Match run | User clicks "Find grants" | One profile; many matches |
| Match | One per grant scored in a run | One match run + one grant |
| Application | User saves a match to the tracker | One profile + one grant; many notes |
| Note / status change | User updates an application | One application |

The main linked chain is: profile → match run → match → application → status changes. All of these must survive a restart. They live in a database, not in memory, so a user can close the browser and return to their tracker and past results.

---

## Searchable Text

- Grant descriptions: a user may search for "money for kupuna food programs" when the listing says "senior nutrition services." Keyword search would miss that.
- Application notes: for example, "which grants did the funder say to reapply next year?"

Later in the semester, I will compare semantic search with keyword search on these two kinds of text.

---

## Human Review

- Extracted profile: the user must confirm or edit the fields before any matching runs.
- Each match: shown with the quoted eligibility sentence and a link to the original listing so the user can check the source themselves.
- Uncertain matches: if the model sets `needs_review`, or the grant text is unclear, the match is labeled "Needs review" instead of "Strong fit."
- Saving and status changes: happen only when the user clicks. The app never changes an application on its own.

---

## One Failure Case

**What fails:** the LLM call times out or returns output that does not match the expected fields while scoring grants.

**What the user sees:** "We couldn't score 3 of 30 grants. They are listed under Needs review with a link to the original listing." The other results still display.

**What must remain unchanged:** the confirmed profile, earlier match runs, and every saved application and note. A failed run never overwrites or deletes saved records.

---

## Acceptance Criteria

1. Given a confirmed profile for an O'ahu 501(c)(3) and a grant whose deadline was yesterday, when the user runs a match, that grant does not appear in the matches and appears only under "Closed."
2. Given a profile marked "fiscally sponsored, not a 501(c)(3)" and a grant that requires 501(c)(3) status, when the user runs a match, the grant is excluded and the reason "requires 501(c)(3)" is shown.
3. Failure case: Given a user with 2 saved applications, when the LLM call fails during a new match run, the user sees an error with the unscored grants listed under Needs review, and both saved applications and their notes remain unchanged.

---

## Outside Version One

- Automatically crawling or scraping grant websites (version one uses a hand-collected spreadsheet)
- Drafting full grant applications or proposal narratives
- Deadline reminder emails or notifications
- Multiple users or team sharing within one organization
- Grants outside Hawaii, except a few federal listings
- Real organization financial data

---

## Feedback Incorporated

The proposal received positive feedback and two specific suggestions that fit naturally into the design:

- Retrieval before scoring: before running LLM scoring on every remaining listing, the app will first use semantic search over grant descriptions to pull the top candidate grants for a given organization profile. This keeps the system more scalable as the grant database grows and aligns with the planned Embeddings and RAG work.
- Stale listings: because grant deadlines and requirements can change yearly, each listing will store a `retrieved_on` date and display it next to the deadline so users know the information may need to be rechecked against the source.

---

## Open Questions

### Decisions I need to make

- Should the target user be one focus area (for example, education nonprofits only) or all small Hawaii nonprofits?
- Should one user manage one organization profile, or several (for example, a consultant)?
- How should matches be ranked: fit first or deadline first?

### Technical details I will learn later

- Which database and hosting setup to use (covered in the Databases and Docker/Cloud units)
- How to store and search embeddings for grant descriptions (Embeddings unit)

### Feasibility uncertainties

- Can I collect 20+ usable Hawaii grant listings? Investigation: spend 2 hours collecting listings into the spreadsheet. Evidence needed: at least 20 listings with a clear deadline and eligibility text.
- Does the LLM extract eligibility rules accurately? Investigation: run extraction on 10 listings and compare with my own reading. Evidence needed: correct fields on at least 8 of 10.

---

## Next Investigation

The biggest uncertainty is whether finding grants or keeping track of them is the real pain point for small nonprofits.

**Who can answer it:** one or two staff members at a Hawaii nonprofit who apply for grants.

**Evidence I will collect:** a 20-minute interview covering where they look for grants now, how long a search takes, how they track deadlines, and the last grant they missed and why. I will also ask them to rate 3 of my synthetic profiles for realism.

**How it could change scope:** if tracking is the bigger problem, I will make the tracker the center of version one and simplify matching. If eligibility reading is the bigger problem, I will put more effort into match reasons and quoted text.
