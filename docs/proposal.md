# Grant Finder

## Project goal

A grant finder and tracker that helps staff at small Hawaii nonprofits find grants they are eligible for, see why each one fits, and track their applications in one place.

## Intended user and problem

The user is a program or development staff member at a small Hawaii nonprofit (under about 10 staff) working in education, culture, food, or the environment.

Grant-seeking is usually only part of that person's job, not their whole job. Today it is difficult to manage because:

- Grant listings are spread across foundation websites, county pages, PDFs, and Grants.gov, with no single place to check.
- Eligibility rules are written in long, vague prose, so deciding whether an organization qualifies means reading every listing in full.
- Deadlines and application status are tracked in personal spreadsheets or email, so opportunities are missed.

To confirm this workflow, I will interview one nonprofit staff member about how they search for grants now.

## Example input

An organization description the user types in plain language:

> "We're a 501(c)(3) on O'ahu with 4 staff. We run after-school coding and Hawaiian culture programs for about 60 middle schoolers in Waianae. Annual budget is around $350k. We want money for laptops and a summer program next year."

The app turns this into structured fields:

- org type = 501(c)(3)
- island = O'ahu
- focus = youth education, STEM, Hawaiian culture
- population = middle school students
- budget = about $350k
- needs = equipment, summer programming

## Sample input set

The org profiles below are synthetic. The grant listings they are matched against are real public listings.

| # | Input (org profile, summarized) | Expected result |
|---|---|---|
| 1 | O'ahu 501(c)(3), youth coding + Hawaiian culture, $350k budget | Youth education and STEM grants ranked first; grants restricted to other islands excluded |
| 2 | Hawai'i Island food bank, $1.2M budget | Food security grants matched; youth-only grants ranked low |
| 3 | Maui wildfire recovery group, fiscally sponsored (not a 501(c)(3)) | Grants that require 501(c)(3) status excluded, with the reason shown |
| 4 | Kaua'i watershed restoration nonprofit | Environmental and conservation grants matched |
| 5 | Hawaiian language immersion school support group | Culture, language, and education grants matched |
| 6 | Profile with no island or location given | App asks for the location before matching (no guess) |
| 7 | Profile whose only good match has a deadline that already passed | That grant not shown as a match; listed under "Closed" instead |
| 8 | Very short profile: "we help kupuna" | App asks follow-up questions (org type, island, budget) before matching |

## Expected result and value

Afterward, the user sees a ranked list of grants they likely qualify for. Each grant shows:

- the amount
- the deadline
- a one-line reason it fits
- the exact eligibility sentence the reason is based on

They can save a grant to their tracker and update its status as they apply.

This is valuable because a nonprofit staff member can save time while avoiding missed opportunities. The app should help by making the matching process faster and more consistent than reading every grant listing manually.

## Big-picture sketch

The user starts in the profile form, confirms the extracted fields, reviews matches, and saves the relevant grants to a tracker.

## Workflow summary

1. User enters a plain-language description of their organization.
2. The app extracts structured fields like org type, island, focus area, budget, and needs.
3. The app matches those fields against public grant listings.
4. The app ranks the most relevant grants and shows why they match.
5. The user can save grant opportunities and track progress toward applying.

## Data source

The grant listings come from public grant opportunities, such as foundation pages, county and state funding pages, PDFs, and Grants.gov. The organization profile is user-entered and synthetic for testing.

## Up to three core features

1. Turn a plain-language nonprofit profile into structured fields.
2. Rank and explain the most relevant grant matches based on eligibility criteria.
3. Save and track grant opportunities in a tracker with status updates.

## Acceptance criteria

1. Given a nonprofit profile for a 501(c)(3) youth education nonprofit on O'ahu, when the user enters a description, then the app extracts the organization type, island, focus area, and budget correctly.
2. Given that same nonprofit profile, when the user requests matches, then the app shows the relevant grants first and filters out ineligible matches with a reason.
3. Given a profile with no island or location, when the user runs the matching flow, then the app asks for location before matching instead of guessing.

## Open questions

- Confirm which grant sources matter most to nonprofit staff in Hawaii.
- Interview one nonprofit staff member to verify the real grant-search workflow.
- Decide whether matching should be rule-based, AI-assisted, or a mix of both.
