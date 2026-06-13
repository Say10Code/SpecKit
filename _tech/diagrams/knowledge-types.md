# Knowledge Types and Their Relationships

```mermaid
graph TD
    SPEC[Specification PDF]
    
    SPEC -->|SpecExtractor| TXT[Extracted TXT]
    TXT -->|Reviewer checks| WIKI
    
    TXT -->|extracted facts| REFERENCE[Reference Tables]
    TXT -->|read + summarize| SUMMARY[Summary 48 files]
    
    REFERENCE -->|verified values| CONCEPT
    
    SUMMARY -->|extract key ideas| CONCEPT[Concepts 24 files]
    SUMMARY -->|identify orgs| ENTITY[Entities 7 files]
    
    CONCEPT -->|cross-analyze| SYNTHESIS[Syntheses 30 files]
    ENTITY -->|cross-analyze| SYNTHESIS
    REFERENCE -->|cross-analyze| SYNTHESIS
    SUMMARY -->|cross-analyze| SYNTHESIS
    
    SYNTHESIS -->|deep dive| RESEARCH[Research 9 files]
    CONCEPT -->|deep dive| RESEARCH
    REFERENCE -->|deep dive| RESEARCH
    
    WIKI[wiki/ knowledge graph]
    
    RESEARCH --> WIKI
    SYNTHESIS --> WIKI
    CONCEPT --> WIKI
    ENTITY --> WIKI
    SUMMARY --> WIKI
    REFERENCE --> WIKI
```

## Volume / Depth matrix

```
                    Volume (KB)
                    1-3    5-10    10-15    15-50+
Depth               -----------------------------
  extracted         Summary
  foundation                 Entity
  intermediate               Concept
  advanced                         Synthesis
  expert                                  Research
  reference               Reference
```
