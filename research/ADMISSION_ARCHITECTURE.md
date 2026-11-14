# Future research admission architecture — design only

Phase 3E does not admit external sources, write to the approved corpus, or expose a public **Add Research** control. A future admission service requires a verified discovery provider, authenticated reviewer roles, durable staging storage and an approval policy before deployment.

The proposed sequence is:

1. Discover a candidate from an allowlisted official source connector and record its stable URL, publisher, identifier and retrieval time.
2. Resolve source identity against official metadata; store a content hash and immutable original file in staging.
3. Record license/rights evidence and the permitted use of text, tables and media. Unknown rights stay blocked.
4. Check domain, investigation and topic relevance. Separate descriptive background, historical incidents and original experiment data.
5. Extract source passages or measurement tables with exact page/section and original values/units; record extraction method and uncertainty.
6. Detect duplicate sources and overlapping test identifiers using stable IDs, URLs and hashes.
7. Run schema, unit, range, provenance, missing-value and source-link validation. Any mismatch enters a review queue.
8. Require a human reviewer to inspect the original source and approve each admission decision. An LLM assertion cannot satisfy identity, rights or scientific validation.
9. Commit an append-only corpus version with transaction boundaries, reviewer identity, timestamps and an audit log of changed records.
10. Retain prior immutable versions and provide an authorized rollback that changes the active version pointer while preserving audit history.

Only after a successful durable admission should the interface notify users that new verified research was added. Discovery, staging and pending review must never show that success message. Production credentials, reviewer controls and automated admission remain Step 4 work.
