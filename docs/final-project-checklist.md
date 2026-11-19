# Final Project Checklist

## Feature PR

- [x] Create a feature branch (`feature/deadline-status`)
- [x] Implement a focused, testable feature (deadline status: open / closed / unknown)
- [x] Add tests for the new behavior
- [x] Run checks: `uv run pytest`, `uv run ruff check`, `uv run mypy`
- [x] Open a PR describing what the feature does and how it was verified ([PR #2](https://github.com/HokulaniTopping/grant-finder/pull/2))
- [x] PR reviewed and merged

## Skill PR

- [x] Create a skill branch (`skill/pr-prep`)
- [x] Add the skill file (`.github/skills/pr-prep/SKILL.md`)
- [x] Keep the skill clear, structured, and focused
- [x] Open a PR describing the skill's purpose and how to use it ([PR #3](https://github.com/HokulaniTopping/grant-finder/pull/3))
- [x] PR reviewed and merged

## Cleanup

- [ ] Remove the stray `Grant Finder_ ICS 603 Final Project Proposal (1).md` from the repo root (duplicate of `docs/proposal.md`)

## Database (take-home guide: Design Your Project's Database)

Done when `db/migrations/`, `db/seed.py`, `db/queries.py`, `tests/test_queries.py`, and `.env.example` are merged through a PR, `npx dbmate status` shows `Pending: 0`, sample rows are loaded, and `uv run pytest` passes.

### Before starting
- [ ] Add a **Saved records** answer to `docs/proposal.md` naming at least two linked kinds of records the app must remember after it stops (it isn't there yet)

### Step 1: Create the database
- [ ] Create a new Neon project just for Grant Finder
- [ ] Put `DATABASE_URL` and `DBMATE_NO_DUMP_SCHEMA=true` in `.env`
- [x] Confirm `.env` is in `.gitignore`
- [ ] Create `.env.example` with sample values only (committed)
- [ ] `uv add "psycopg[binary]" python-dotenv`
- [ ] Confirm `npx --version` works

### Step 2: Design the data model
- [ ] Use the brainstorming skill to decide entities, attributes, relationships (one-to-many / many-to-many / one-to-one), required and unique values, and ON DELETE behavior
- [ ] Answer each design question yourself (entity or attribute? how many on each side? needed now?)
- [ ] Write the approved decisions into `docs/proposal.md` (no separate spec, no code yet)

### Step 3: Write the first migration
- [ ] `npx dbmate new create_tables`
- [ ] Have the agent write raw SQL under `-- migrate:up`, leaving `-- migrate:down` empty

### Step 4: Review the schema before running it
- [ ] Every table has a primary key
- [ ] Every relationship is a foreign key (no parent names stored as text)
- [ ] No column stores a list
- [ ] Required columns are `NOT NULL`
- [ ] Values that must not repeat are `UNIQUE`
- [ ] Junction tables have a composite primary key
- [ ] Foreign-key columns that are filtered or joined on have an index
- [ ] Every table is needed now
- [ ] Moments use `timestamptz`, calendar dates use `date`
- [ ] Each column's type matches its values
- [ ] Every foreign key states its `ON DELETE` behavior

### Step 5: Run the migration
- [ ] `npx dbmate status` shows the file pending
- [ ] `npx dbmate migrate`
- [ ] `npx dbmate status` shows `Pending: 0`

### Step 6: Load sample data
- [ ] Write `db/seed.py` (stops if rows exist, one transaction, `RETURNING id`, `%s` parameters, 3–8 rows per table)
- [ ] Sample rows include a parent with no children, a parent with several, a NULL optional column, and long text or an apostrophe (e.g. "O'ahu")
- [ ] Read it, then run `uv run python db/seed.py` once

### Step 7: Write the test first
- [ ] Pick one question the app asks its data
- [ ] Add a stub in `db/queries.py` that raises `NotImplementedError`
- [ ] Write `tests/test_queries.py` with a rollback fixture and `skipif` when `DATABASE_URL` is not set
- [ ] Run `uv run pytest` and confirm it fails at `NotImplementedError` (red)

### Step 8: Write the query
- [ ] Implement the function with `%s` parameters and a one-line docstring, without changing the test
- [ ] Run `uv run pytest` and confirm it passes (green)

### Step 9: Pull request
- [ ] Commit on a branch: `db/migrations/`, `db/seed.py`, `db/queries.py`, `tests/test_queries.py`, `.env.example`, `docs/proposal.md`, `pyproject.toml`, `uv.lock`
- [ ] PR description lists each relationship and its kind
- [ ] Confirm `.env` is not in the diff
- [ ] Merge after review

### Rules going forward
- Every schema change is a new migration; never edit one that has already run
- Never run `dbmate rollback`
- Make a Neon branch before any migration that deletes data

## Proposal coverage (`docs/proposal.md`)

Everything the proposal promises, so the finished app covers all of it.

### Research and open questions
- [ ] Interview one Hawaii nonprofit staff member about how they search for grants now
- [ ] Confirm which grant sources matter most to them
- [ ] Decide whether matching is rule-based, AI-assisted, or a mix, and record the decision in the proposal
- [ ] Add a **Saved records** answer to the proposal (also needed for the database work)

### Grant data
- [ ] Collect a set of real public grant listings (foundation pages, county/state pages, PDFs, Grants.gov) covering education, culture, food, and environment
- [ ] Each listing records: amount, deadline, island/location restriction, org-type requirement (e.g. 501(c)(3) only), focus areas, and the exact eligibility sentence
- [ ] Store listings so the app can match against them

### Core feature 1: Profile → structured fields
- [ ] Profile form where the user types a plain-language description (form exists, not wired up yet)
- [ ] `app/agent.py` extracts org type, island, focus areas, population, budget, and needs
- [ ] User can review and confirm the extracted fields before matching
- [ ] If location is missing, ask for it instead of guessing (`requires_location` rule exists; not connected to the flow yet)
- [ ] If the profile is too short (e.g. "we help kupuna"), ask follow-up questions for org type, island, and budget

### Core feature 2: Rank and explain matches
- [ ] Island/location eligibility rule: exclude grants restricted to other islands
- [ ] Org-type eligibility rule: exclude 501(c)(3)-only grants for fiscally sponsored groups, with the reason shown
- [x] Deadline rule: open / closed / unknown (`deadline_status`, PR #2)
- [ ] Closed grants are not shown as matches and are listed under "Closed" instead
- [ ] Rank eligible grants by fit to focus areas and needs
- [ ] Each match shows the amount, the deadline, a one-line reason it fits, and the exact eligibility sentence that reason is based on
- [ ] Excluded grants show why they were excluded
- [ ] `/api/grants` returns real matches instead of the placeholder

### Core feature 3: Save and track
- [ ] User can save a grant to their tracker
- [ ] User can update a saved grant's application status
- [ ] Tracker page lists saved grants with deadline and status
- [ ] Saved grants and statuses are stored in the database

### Sample input set (proposal table)
Each case should have a test or a recorded check.
- [ ] 1. O'ahu 501(c)(3), youth coding + culture: youth education and STEM grants ranked first; other-island grants excluded
- [ ] 2. Hawai'i Island food bank: food security grants matched; youth-only grants ranked low
- [ ] 3. Maui fiscally sponsored group: 501(c)(3)-only grants excluded with the reason shown
- [ ] 4. Kaua'i watershed nonprofit: environmental and conservation grants matched
- [ ] 5. Hawaiian language immersion support group: culture, language, and education grants matched
- [ ] 6. No island or location: app asks for location before matching (rule done; flow not yet)
- [ ] 7. Only good match is past deadline: grant shown under "Closed", not as a match (rule done; flow not yet)
- [ ] 8. "we help kupuna": app asks follow-up questions before matching

### Acceptance criteria
- [ ] AC1: For the O'ahu 501(c)(3) youth education profile, org type, island, focus area, and budget are extracted correctly
- [ ] AC2: For that profile, relevant grants come first and ineligible ones are filtered out with a reason
- [ ] AC3: With no island or location, the app asks for location before matching

### End-to-end workflow
- [ ] A user can go from profile form → confirm fields → review matches → save to tracker → update status, all in the running app

## Additional requirements

<!-- To be filled in from the remaining final project requirements. -->
