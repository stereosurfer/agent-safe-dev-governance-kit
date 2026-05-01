# Externalized Responsibility Boundary

## Purpose

Prevent scope creep by defining responsibilities that belong outside this repository.

## External Preparation App

Raw, messy, private, or rights-sensitive materials should be prepared outside this repository.

```text
External Preparation App / manual workflow
  raw PDFs / scans / OCR / messy files / browser captures / private folders
  -> cleaned prepared input
  -> safe metadata
  -> locators
  -> redaction and rights notes
  -> reviewed context pack

This repository
  prepared input / source registry / reviewed context pack
  -> validation
  -> promotion gate
  -> output-eligible artifacts
```

## Closed gates

This boundary does not authorize:

- raw PDF ingestion inside this repository;
- OCR inside this repository;
- scan cleanup inside this repository;
- private corpus folder ingestion;
- raw browser capture retention;
- raw media retention;
- automatic claim promotion from prepared material;
- publication.

## Required prepared input metadata

Prepared inputs should carry:

- safe title or label;
- creator / publisher when safe;
- rights and access notes;
- privacy/redaction status;
- locator scheme;
- preparation method;
- content boundaries;
- claim-use caveats.
