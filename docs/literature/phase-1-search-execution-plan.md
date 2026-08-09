# Phase 1 search execution plan

**Protocol:** `phase-1-review-protocol.md` v0.1  
**Status:** Operational package; searches still need to be run and logged  
**Prepared:** 2026-08-09

## Purpose

This document turns the Phase 1 protocol into a reproducible execution sheet.
It does not replace the protocol and does not count a search as completed until
the exact query, filters, result count and export file are recorded in
`search-log.csv`.

## Search blocks

The searches use three concept blocks. The first two are required; the third is
used for a targeted human/engineering-practice search.

```text
A = ("continuous delivery" OR "continuous deployment" OR DevOps OR "continuous software engineering")
B = (reliab* OR resilien* OR dependab* OR incident* OR failure* OR recover* OR rollback OR "self-healing" OR "fault injection" OR "chaos engineering")
C = (automat* OR engineer* OR operator* OR decision* OR workload OR trust OR diagnosis OR mitigation OR "incident response")
```

### Core search

```text
A AND B
```

### Human/engineering-practice search

```text
A AND B AND C
```

The human search is additive. It must not replace the broader search because
technical studies may not use human-factor terminology in their title or
abstract.

## Database execution sheet

Run each source separately. Copy the exact query submitted to the database,
including field restrictions and date/language filters, into `search-log.csv`.
Record the export filename before deduplication.

| Search ID | Source | Query field mapping | Required record |
|---|---|---|---|
| S001 | ACM Digital Library | Abstract/title/keyword search using A and B; repeat with C if supported | Query, date/time, filters, result count, export filename |
| S002 | IEEE Xplore | Metadata search using A and B; repeat with C | Query, date/time, filters, result count, export filename |
| S003 | Scopus or Web of Science | Title/abstract/keyword fields using A and B; repeat with C | Which index was used, query, date/time, filters, count, export filename |
| S004 | Google Scholar | Backward and forward citation chasing from included/secondary records | Seed paper, direction, date, screened candidates and decision |
| S005 | Author/institution repositories | Full-text retrieval for candidate records | URL, access date, version checked and full-text status |

Do not enter a count obtained from a search-result snippet or a later rerun
under the original search ID. Create a new search ID and preserve both
records.

## Pilot and screening sequence

1. Run the two core database searches and export the records.
2. Deduplicate using DOI, then normalised title plus first author/year.
3. Pilot title/abstract screening on the first 20 deduplicated records.
4. Record any eligibility-rule change in the protocol changelog before full
   screening.
5. Screen the complete deduplicated set.
6. Retrieve full texts for all records marked `include` or `uncertain`.
7. Record one primary exclusion reason for every full-text exclusion.
8. Chart included studies using the extraction guide and update the matrix only
   after checking the cited full text.

## Reproducibility checklist

For every completed search, retain:

- database or source name;
- account/institution context when access affects results;
- UTC search timestamp;
- exact query string;
- field restrictions;
- date, language and publication-type filters;
- result count before deduplication;
- export format and filename;
- deduplication method and resulting count; and
- any access or indexing limitation.

The repository may contain metadata and legally obtained full texts, but it
must not commit copyrighted database exports or restricted papers unless the
licence permits it.

## Stop conditions

Pause and record an issue rather than silently changing the review when:

- a database does not support the planned syntax;
- a source returns no results because a field restriction is unavailable;
- the same result set cannot be exported reproducibly;
- the full text cannot be obtained after reasonable repository/author search;
- a record's empirical status cannot be determined from the available text; or
- the 20-record pilot suggests that the eligibility boundary is unclear.

The current repository remains incomplete until the resulting logs and matrix
contain the evidence needed by the Phase 1 exit criteria.
