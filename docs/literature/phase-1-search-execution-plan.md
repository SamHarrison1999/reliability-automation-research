# Phase 1 database search strategy and execution plan

**Protocol:** `phase-1-review-protocol.md` v1.0
**Strategy version:** 1.0
**Prepared:** 2026-08-09
**Status:** Finalised for platform smoke-testing; no result count has been recorded

## 1. Search architecture

The strategy uses three complementary families. Each family is run separately
in ACM Digital Library, IEEE Xplore and the selected multidisciplinary index.
This preserves recall and makes each evidence strand auditable.

### Family T — technical mechanisms and outcomes

Purpose: identify empirical evaluations of detection, rollback, remediation,
recovery, containment, resilience testing and related mechanisms.

```text
T-CONTEXT =
  "continuous delivery" OR "continuous deployment" OR DevOps OR SRE OR
  "site reliability engineering" OR "cloud native" OR cloud-native OR
  microservice* OR "online service*" OR "distributed system*"

T-MECHANISM =
  "reliability automation" OR "incident response automation" OR
  "automated incident response" OR "automated remediation" OR
  "automatic remediation" OR "automated recovery" OR "automatic recovery" OR
  self-heal* OR "automated rollback" OR "automatic rollback" OR failover OR
  AIOps OR "fault injection" OR "chaos engineering" OR "resilience testing"

T-OUTCOME =
  reliab* OR resilien* OR dependab* OR availab* OR incident* OR failure* OR
  fault* OR detect* OR diagnos* OR recover* OR restor* OR contain* OR mitigat* OR
  rollback OR "service impact" OR "mean time to recover" OR
  "mean time to repair" OR MTTR

T = T-CONTEXT AND T-MECHANISM AND T-OUTCOME
```

Likely omissions: papers that describe an automation mechanism only by a tool
name, use domain-specific dependability terms, or omit continuous-delivery and
cloud terminology. Mitigation: seed-paper testing, citation chasing and a
documented candidate-term register; do not silently edit T.

### Family H — engineering practice and human–automation interaction

Purpose: identify direct or operational evidence about engineers' incident
work, decisions, workload, understanding, trust and reliance.

```text
H-CONTEXT =
  DevOps OR SRE OR "site reliability engineering" OR "continuous delivery" OR
  "continuous deployment" OR "incident response" OR "incident management" OR
  on-call OR "online service*" OR "cloud native" OR cloud-native OR
  microservice*

H-AUTOMATION-WORK =
  automat* OR AIOps OR observab* OR monitor* OR alert* OR triage OR diagnos* OR
  remediat* OR recover* OR rollback OR "decision support" OR self-heal*

H-HUMAN =
  engineer* OR operator* OR practitioner* OR human OR "human in the loop" OR
  human-in-the-loop OR decision* OR workload OR "cognitive load" OR trust OR
  reliance OR calibrat* OR "situation awareness" OR understand* OR explain* OR
  escalat* OR coordinat* OR collaboration OR "manual intervention"

H = H-CONTEXT AND H-AUTOMATION-WORK AND H-HUMAN
```

Likely omissions: ethnographic or organisational studies that do not use an
automation term in searchable metadata, and human-factors studies outside
software operations. Mitigation: citation chasing from included human studies
and explicitly justified adjacent sources. General automation-trust research is
not automatically eligible.

### Family M — methods, measurement and reproducibility

Purpose: identify empirical and methodological work that informs controlled
fault experiments, metric validity, benchmark selection and reproducibility.

```text
M-CONTEXT =
  "software engineering" OR DevOps OR SRE OR "cloud native" OR cloud-native OR
  microservice* OR "distributed system*" OR "online service*"

M-EXPERIMENT =
  "fault injection" OR "chaos engineering" OR "resilience testing" OR
  "controlled experiment" OR benchmark* OR "incident dataset" OR
  "recovery experiment"

M-METHOD =
  reproducib* OR replicab* OR valid* OR "experimental design" OR
  operationali* OR measur* OR metric* OR workload OR reset OR contamination OR
  provenance OR "mixed methods" OR "threats to validity"

M = M-CONTEXT AND M-EXPERIMENT AND M-METHOD
```

Likely omissions: generic empirical-software-engineering guidance and older
human-factors measurement literature. Such sources may be added to a separate
methodological/contextual register when directly required, but they are not
counted as empirical reliability-automation studies.

## 2. Database translations

Search interfaces change. The reviewer must use the named platform's advanced
or command search, preserve the interface-generated query verbatim, and never
claim execution from the templates alone.

### 2.1 ACM Digital Library

Use Advanced Search. Place each family in title/abstract/keyword or equivalent
metadata fields supported by the current interface; do not search full text for
the primary run because it is less comparable with IEEE and Scopus/Web of
Science metadata searches. Enter the Boolean family exactly as defined above,
then record the complete ACM-rendered query.

Apply filters after recording the unfiltered count:

- publication date: 2010 through the execution date;
- content type: research articles/proceedings papers, retaining empirically
  grounded experience reports; and
- language: English where the interface supports it, otherwise screen language
  later.

Run and log T, H and M separately.

### 2.2 IEEE Xplore

Use Command Search or Advanced Search with metadata fields. IEEE Xplore searches
metadata by default; limit the query to document title, abstract and index terms
where the interface permits. Preserve the exact command generated or submitted.

Apply:

- publication years 2010 through the execution year;
- journals and conferences; and
- English where an explicit filter exists.

Run and log T, H and M separately. Do not use a leading `+` syntax unless the
current IEEE interface itself generates and documents it.

### 2.3 Scopus

If Scopus is the selected multidisciplinary index, use this structure for each
family, substituting the expanded Boolean family inside the field function:

```text
TITLE-ABS-KEY(<FAMILY>)
AND PUBYEAR > 2009
AND PUBYEAR < <execution-year-plus-one>
AND (LIMIT-TO(LANGUAGE, "English"))
```

Record the exact final string, Scopus database coverage shown by the platform,
date/time, filters and result count. Do not use an execution-year placeholder in
the logged query.

### 2.4 Web of Science Core Collection

If Web of Science is selected, use Topic for each family:

```text
TS=(<FAMILY>)
AND PY=(2010-<execution-year>)
AND LA=(English)
```

Record the exact edition/indexes searched (for example, Core Collection indexes)
and timespan. Do not label a search simply “Web of Science” without the database
and platform details.

### 2.5 Supplementary identification

For every included primary study and eligible secondary review:

- inspect the reference list for earlier candidates;
- perform forward citation searching in an accessible citation index;
- record seed `paper_id`, direction, date, tool/index and number screened; and
- route candidates through the same screening criteria.

Use Google Scholar only for this documented supplementary purpose or to locate a
known item. Result estimates from Google Scholar are not treated as stable
database-search counts.

## 3. Smoke test before counted execution

The smoke test checks translation, not eligibility or synthesis.

1. Run each family without saving its count as the final execution record.
2. Check whether the platform can retrieve multiple conceptually relevant seed
   records where those records are indexed.
3. Inspect the first 20 results for obvious precision failure.
4. Record missing terms, syntax errors and interface limitations in a test note.
5. If a family changes, increment the strategy version and record the amendment.
6. Execute the final version once per platform and preserve its export/count.

Do not tune a query solely until all nine seeds appear. Seed records test gross
recall; they do not define the eligible universe.

## 4. Execution order

1. Confirm access to ACM Digital Library, IEEE Xplore and Scopus/Web of Science.
2. Freeze protocol v1.0 and strategy v1.0, or record a prospective amendment.
3. Smoke-test T, H and M on each platform.
4. Execute all final database searches on the same day where practical.
5. Record each exact query and count before export.
6. Export complete metadata/abstracts and record filename, format and hash.
7. Import all exports without modifying them.
8. Deduplicate by DOI, title and author/year rules.
9. Run the 20-record screening pilot.
10. Amend decision rules prospectively if required, then screen the full set.
11. Retrieve and assess full texts.
12. Perform backward/forward citation chasing after an initial included set is
    available, then rerun deduplication and screening for added records.

## 5. Required search-log fields

Each executed search record must include:

- stable `search_id`;
- search family and version;
- database and platform/interface;
- coverage/indexes;
- UTC and local timestamps;
- exact query;
- fields and filters;
- count before deduplication;
- export filename, format and hash;
- execution status; and
- limitations or deviations.

Create a new row for every rerun. Never replace an earlier count or retroactively
put a new query under an old `search_id`.

## 6. Search IDs reserved for v1.0

| Search ID | Family | Source | Status |
|---|---|---|---|
| S001 | T | ACM Digital Library | planned |
| S002 | T | IEEE Xplore | planned |
| S003 | T | Scopus or Web of Science Core Collection | access decision pending |
| S004 | H | ACM Digital Library | planned |
| S005 | H | IEEE Xplore | planned |
| S006 | H | Scopus or Web of Science Core Collection | access decision pending |
| S007 | M | ACM Digital Library | planned |
| S008 | M | IEEE Xplore | planned |
| S009 | M | Scopus or Web of Science Core Collection | access decision pending |
| S010+ | Citation chasing | Included/secondary seed-specific searches | pending included set |
| S900 | Seed identification | Existing web-assisted nine-record map | completed as seed only; not a database run |

## 7. Stop conditions

Pause and document the issue when:

- institutional access or export capability is missing;
- a field mapping changes the meaning of a family;
- the interface rejects or silently truncates a query;
- a search produces zero results because syntax or fields are unsupported;
- the export omits essential metadata and cannot be reproduced;
- the 20-record pilot exposes an ambiguous eligibility boundary; or
- the reviewer cannot verify a record or citation from a primary source.

Do not compensate for a blocked database by presenting ordinary web search as
equivalent coverage.
