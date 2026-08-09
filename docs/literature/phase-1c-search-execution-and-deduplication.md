# Phase 1C — search execution and deduplication

**Project:** An Empirical Investigation of Reliability Automation and Software Engineering Practice in Continuous Delivery Environments
**Execution date:** 2026-08-09
**Branch intended for:** `research/phase-1-literature-evidence`
**Stage status:** supplementary discovery and provisional deduplication completed; authenticated named-database execution remains pending

## 1. Scope of this stage

This stage follows the Phase 1B supplementary evidence batch. It has two
purposes:

1. extend candidate discovery into the human/practice and continuous-delivery
   strands that were underrepresented in the first batch; and
2. apply the planned DOI-first, then normalised-title/author/year
   deduplication rule to the records already present in the repository.

The public discovery searches are recorded for provenance, but they are not
counted as ACM Digital Library, IEEE Xplore, Scopus or Web of Science coverage.
Public search-result counts are not stable enough to enter as database counts,
and no licensed export was available in this workspace.

## 2. Searches executed

The supplementary search rows are in `search-log-batch-02.csv`. They record
the exact query text used, the interface, date and access limitation. The
searches identified five additional candidate records:

- direct engineer and incident-response evidence;
- human cognitive/practice context;
- learning from failure and postmortem work; and
- controlled continuous deployment in a high-reliability embedded domain.

The most directly relevant additions are not treated as interchangeable. The
incident-response studies provide evidence about engineers, incident reports,
diagnosis, mitigation and organisational learning. They do not automatically
provide validated workload, trust or decision-quality measures, and they do not
constitute controlled comparisons of reliability-automation strategies.

## 3. Authenticated database status

The planned ACM, IEEE and multidisciplinary-index searches remain
`pending_access_or_export`. The exact queries are recorded in the search log so
that the user can execute them in an authenticated institutional session and
append the returned count, export filename, format and SHA-256 hash.

The following must not be inferred from this stage:

- a total number of ACM, IEEE, Scopus or Web of Science records;
- database coverage from ordinary web-search ordering;
- a final prevalence estimate for human-factor studies; or
- completion of the PRISMA flow.

## 4. Deduplication method

The deduplication register applies the protocol rule in this order:

1. normalised DOI, where a DOI is present;
2. exact or near-exact normalised title plus first author and publication year;
3. manual review of possible version relationships, such as an arXiv record
   and the corresponding conference publication.

The canonical identifier is retained from the existing repository record when
the record is already in the seed matrix or Phase 1B evidence batch. Candidate
records that were not yet assigned a canonical paper ID are mapped to the next
available stable ID in the deduplication register.

The results are in:

- `deduplication-log-batch-02.csv` — one decision per canonical source group;
- `deduplicated-source-register-batch-02.csv` — the source-level queue for the
  next screening stage; and
- `canonical-id-corrections-batch-02.csv` — the required P21-to-P09 correction
  before screening;
- `prisma-flow-batch-02.csv` — incremental bookkeeping only, not final PRISMA
  totals.

## 5. Decisions made

- C10 duplicates P10; retain P10 and merge the candidate provenance.
- C12–C19 duplicate P12–P19 respectively; retain the existing evidence IDs.
- C21 duplicates P21; retain P21 and merge the candidate provenance.
- C11, C20 and C22 are retained as distinct candidate records and reserved as
  P11, P20 and P22 pending title/abstract screening and full-text status.
- C23–C27 are new candidate records and are provisionally assigned P23–P27.
- No record is promoted to the canonical evidence matrix by this stage alone.

## 6. Outstanding work

1. Run S001–S003 in the authenticated database platforms and append the actual
   counts and export hashes.
2. Import the licensed exports locally without committing them unless the
   licence permits repository storage.
3. Re-run deduplication over the database exports and the canonical source
   register.
4. Pilot title/abstract screening on 20 deduplicated records.
5. Record any protocol amendment before screening the remainder.

This document is an evidence-stage record, not a completed literature review.
