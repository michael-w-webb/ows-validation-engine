# Workbook Parser Test Fixtures

This directory contains intentionally small Excel workbooks used for
testing workbook parsing, schema extraction, header detection, and
session mutation behavior in the workbook parser service.

These fixtures are designed to simulate common real-world workbook
patterns encountered in workforce, grant reporting, and administrative
Excel files.

Fixtures should remain:

- Small
- Deterministic
- Human-readable
- Focused on a specific parsing scenario

The goal is to test parser behavior and edge cases, not large-scale
performance.

---

# Fixture Inventory

## simple_workbook.xlsx

Purpose:
- Baseline parser validation
- Happy-path workbook parsing
- Basic structure extraction

Characteristics:
- Single sheet
- Clean headers
- Standard row structure
- No formatting irregularities

Primary test targets:
- Workbook loading
- Header extraction
- Session creation

---

## multi_sheet_workbook.xlsx

Purpose:
- Multi-sheet parsing validation
- Per-sheet structure extraction

Characteristics:
- Multiple sheets
- Distinct schemas per sheet
- Consistent formatting

Primary test targets:
- Sheet iteration
- Multi-sheet structure aggregation
- Sheet-specific header management

---

## offset_headers.xlsx

Purpose:
- Header row adjustment testing
- Nonstandard workbook layouts

Characteristics:
- Metadata rows before actual headers
- Actual headers begin below row 1

Primary test targets:
- Header row mutation
- Re-parsing workflows
- Future header auto-detection logic

Notes:
This is one of the highest-value parser fixtures because many
real-world administrative workbooks contain title rows,
instructions, timestamps, or merged metadata above the actual schema.

---

## blank_sheet_workbook.xlsx

Purpose:
- Empty workbook handling

Characteristics:
- Empty or nearly empty sheets

Primary test targets:
- Defensive parsing
- Empty schema handling
- Graceful failure behavior

---

## partial_headers.xlsx

Purpose:
- Malformed schema testing

Characteristics:
- Missing header names
- Blank header cells

Primary test targets:
- Header filtering
- Null handling
- Parser resilience

---

## duplicate_headers.xlsx

Purpose:
- Duplicate column detection

Characteristics:
- Repeated header names

Primary test targets:
- Duplicate handling
- Schema normalization
- Future warning generation

Notes:
Duplicate columns are common in manually maintained Excel workbooks.

---

## hidden_sheet_workbook.xlsx

Purpose:
- Hidden worksheet handling

Characteristics:
- Hidden tabs
- Mixed visible and hidden sheets

Primary test targets:
- Sheet visibility handling
- Workbook enumeration logic

---

## merged_header_workbook.xlsx

Purpose:
- Merged-cell workbook handling

Characteristics:
- Merged title/header regions
- Multi-row visual formatting

Primary test targets:
- Header detection robustness
- Worksheet traversal behavior

Notes:
Merged title rows are common in government and reporting spreadsheets.

---

## messy_spacing_workbook.xlsx

Purpose:
- Header normalization testing

Characteristics:
- Irregular spacing
- Mixed capitalization
- Formatting inconsistencies

Primary test targets:
- Text normalization
- Header cleaning
- Canonical schema mapping

---

## corrupted_headers.xlsx

Purpose:
- Corrupted or low-quality schema testing

Characteristics:
- Placeholder columns
- Unnamed columns
- Ambiguous header structure

Primary test targets:
- Parser resilience
- Warning handling
- Schema quality assessment

---

# Fixture Design Principles

Fixtures should:

- Represent a single primary edge case
- Avoid unnecessary complexity
- Remain stable over time
- Be safe for version control
- Be easy to inspect manually

Avoid:
- Large datasets
- Randomized data
- Sensitive information
- Production exports

---

# Future Fixture Categories

As the parser evolves, additional fixtures may be added for:

- Protected workbooks
- Hidden rows/columns
- Formula-heavy workbooks
- Extremely wide schemas
- Multi-level headers
- Inconsistent sheet schemas
- Invalid date formats
- Mixed data typing
- Unicode / encoding edge cases
- OneDrive corruption scenarios

---

# Regression Fixtures

If a production parsing bug is discovered, a minimized reproduction
workbook should be added here whenever possible.

Regression fixtures are especially valuable because they ensure that
previously resolved parsing failures do not silently recur.