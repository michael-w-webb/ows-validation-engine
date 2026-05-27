# OWS Validation Engine

The OWS Validation Engine is a schema-driven data validation and normalization framework designed for workforce development reporting systems. It was originally developed to support Connecticut Office of Workforce Strategy (OWS) reporting workflows, where organizations submit highly variable Excel workbooks that must be standardized, validated, reconciled, and transformed into analysis-ready datasets.

The engine is built to handle inconsistent real-world reporting environments, including:

- Variable column names and workbook structures
- Multi-sheet Excel submissions
- Hidden or protected worksheets
- Missing or malformed values
- Cross-sheet participant reconciliation
- Complex business-rule validation
- Audit logging and error reporting

Rather than relying on hardcoded templates, the system uses configurable workbook definitions and schema objects to dynamically interpret incoming files.

---

## Documentation

Full documentation, architecture walkthroughs, and implementation details are available here:

[OWS Validation Engine Documentation](https://michael-w-webb.github.io/ows-validation-engine/)

---

## Core Features

### Schema-Driven Validation

Validation behavior is controlled through workbook definition objects and typed column classes rather than file-specific scripts.

Supported validation concepts include:

- Required field validation
- Accepted response enforcement
- Type-aware normalization
- Cross-sheet rule evaluation
- Identifier construction and reconciliation
- Dataset merging and reporting

### Flexible Excel Parsing

The engine is designed for noisy operational reporting data and includes support for:

- Dynamic header extraction
- Multiple workbook formats
- Variant column labels
- Hidden/protected worksheet handling
- Inconsistent sheet naming
- Multi-sheet linking logic

### Normalization Pipeline

Typical processing flow:

1. Load workbook
2. Resolve workbook structure
3. Normalize column values
4. Construct deterministic participant identifiers
5. Reconcile participants across sheets
6. Merge normalized datasets
7. Execute validation rules
8. Generate audit/error reports

### Cross-Sheet Rule Engine

The validation system supports recursive cross-sheet dependencies and conditional logic.

Examples include:

- Participant appears in required downstream sheets
- Outcome requires corresponding service records
- Enrollment dates align across datasets
- Employment records satisfy program completion conditions

### Audit Logging

Optional SQLite-backed logging allows tracking of:

- Validation runs
- Participant presence
- Normalized cell values
- Error outputs
- File provenance

---

## Repository Structure

The repository contains components for:

- Excel parsing
- Workbook schema management
- Validation rule execution
- Data normalization
- API services
- Reporting and logging
- Documentation generation
- Frontend schema-management tooling

---

## Primary Use Cases

The engine is particularly well suited for:

- Workforce development reporting
- Grant compliance workflows
- Multi-organization Excel submissions
- Longitudinal participant tracking
- Data quality auditing
- ETL preprocessing pipelines
- Operational reporting systems

---

## Project Status

This repository is under active development. Current work includes:

- Expanded workbook schema tooling
- API-driven validation workflows
- UI-based workbook definition management
- Improved audit logging
- Enhanced cross-sheet reconciliation
- Scalable deployment infrastructure

---

## License

This project is released under the MIT License.

---

## Contributing

Contributions, bug reports, documentation improvements, and feature suggestions are welcome.

Contributors should work from their own branches and submit changes through pull requests. Direct architectural modifications to the core validation pipeline, schema system, reconciliation logic, or workbook-definition framework should not be introduced without prior discussion and approval.

To help maintain consistency and long-term stability:

- Create a dedicated feature or fix branch for all work
- Keep pull requests focused and reasonably scoped
- Include clear descriptions of proposed changes
- Avoid unrelated formatting or whitespace-only changes
- Open an issue before proposing significant architectural adjustments

All pull requests are reviewed before merging.

---

## Additional Resources

- [GitHub Repository](https://github.com/michael-w-webb/ows-validation-engine)
- [Project Documentation Site](https://michael-w-webb.github.io/ows-validation-engine/)