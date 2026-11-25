-- migrate:up
CREATE EXTENSION IF NOT EXISTS vector;

-- One nonprofit profile, reopened through its private access token.
CREATE TABLE organizations (
    id            integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    access_token  text        NOT NULL UNIQUE,
    description   text        NOT NULL,
    name          text,
    org_type      text,
    island        text CHECK (island IN (
                      'oahu', 'maui', 'hawaii', 'kauai', 'molokai',
                      'lanai', 'niihau', 'kahoolawe')),
    location      text,
    population    text,
    budget        integer CHECK (budget >= 0),
    created_at    timestamptz NOT NULL DEFAULT now()
);

-- One public grant listing, with the source behind its eligibility claim.
CREATE TABLE grants (
    id                    integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    slug                  text    NOT NULL UNIQUE,
    name                  text    NOT NULL,
    funder                text    NOT NULL,
    source_url            text    NOT NULL,
    eligibility_sentence  text    NOT NULL,
    amount_text           text    NOT NULL,
    deadline              date,
    deadline_note         text,
    verified              boolean NOT NULL DEFAULT false,
    embedding             vector(1536)
);

-- One grant on one organization's tracker, with its current status.
CREATE TABLE saved_grants (
    id               integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    organization_id  integer NOT NULL REFERENCES organizations (id) ON DELETE CASCADE,
    grant_id         integer NOT NULL REFERENCES grants (id) ON DELETE RESTRICT,
    status           text    NOT NULL DEFAULT 'interested' CHECK (status IN (
                         'interested', 'drafting', 'submitted', 'awarded', 'declined')),
    saved_at         timestamptz NOT NULL DEFAULT now(),
    updated_at       timestamptz NOT NULL DEFAULT now(),
    UNIQUE (organization_id, grant_id)
);
CREATE INDEX saved_grants_grant_id_idx ON saved_grants (grant_id);

-- One topic in the shared vocabulary that grants and organizations both use.
CREATE TABLE focus_areas (
    id    integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name  text NOT NULL UNIQUE
);

-- One thing grant money can pay for, such as equipment or programs.
CREATE TABLE funding_uses (
    id    integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name  text NOT NULL UNIQUE
);

-- One focus area a grant funds.
CREATE TABLE grant_focus_areas (
    grant_id       integer NOT NULL REFERENCES grants (id) ON DELETE CASCADE,
    focus_area_id  integer NOT NULL REFERENCES focus_areas (id) ON DELETE RESTRICT,
    PRIMARY KEY (grant_id, focus_area_id)
);
CREATE INDEX grant_focus_areas_focus_area_id_idx ON grant_focus_areas (focus_area_id);

-- One focus area an organization works in.
CREATE TABLE organization_focus_areas (
    organization_id  integer NOT NULL REFERENCES organizations (id) ON DELETE CASCADE,
    focus_area_id    integer NOT NULL REFERENCES focus_areas (id) ON DELETE RESTRICT,
    PRIMARY KEY (organization_id, focus_area_id)
);
CREATE INDEX organization_focus_areas_focus_area_id_idx
    ON organization_focus_areas (focus_area_id);

-- One thing a grant's money can pay for.
CREATE TABLE grant_funding_uses (
    grant_id         integer NOT NULL REFERENCES grants (id) ON DELETE CASCADE,
    funding_use_id   integer NOT NULL REFERENCES funding_uses (id) ON DELETE RESTRICT,
    PRIMARY KEY (grant_id, funding_use_id)
);
CREATE INDEX grant_funding_uses_funding_use_id_idx ON grant_funding_uses (funding_use_id);

-- One thing an organization needs money for.
CREATE TABLE organization_needs (
    organization_id  integer NOT NULL REFERENCES organizations (id) ON DELETE CASCADE,
    funding_use_id   integer NOT NULL REFERENCES funding_uses (id) ON DELETE RESTRICT,
    PRIMARY KEY (organization_id, funding_use_id)
);
CREATE INDEX organization_needs_funding_use_id_idx ON organization_needs (funding_use_id);

-- One island a grant serves; 'statewide' means every island.
CREATE TABLE grant_islands (
    grant_id  integer NOT NULL REFERENCES grants (id) ON DELETE CASCADE,
    island    text    NOT NULL CHECK (island IN (
                  'statewide', 'oahu', 'maui', 'hawaii', 'kauai', 'molokai',
                  'lanai', 'niihau', 'kahoolawe')),
    PRIMARY KEY (grant_id, island)
);

-- One legal organization type a grant accepts.
CREATE TABLE grant_org_types (
    grant_id  integer NOT NULL REFERENCES grants (id) ON DELETE CASCADE,
    org_type  text    NOT NULL CHECK (org_type IN (
                  '501(c)(3)', 'fiscally sponsored', 'nonprofit', 'public school')),
    PRIMARY KEY (grant_id, org_type)
);

-- migrate:down
