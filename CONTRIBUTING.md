# Contribution Guide — Voxeprint

Thank you for your interest in contributing to Voxeprint! This project is a 3D printing cost calculator, developed in Python with PySide6, following the strict MVP pattern, using SQLite and multi-currency support.

---

## How to contribute?

1. **Fork the repository** and create your branch from `develop`.
2. **Branch flow:**
   - `develop`: main development branch, all changes and new features go here.
   - `release`: stable versions only, merge from `develop` when ready for production.
3. **Branch naming:** use the format `feature/<description>`, `fix/<description>` or `task/<task_name>`.
4. **Follow the architecture (strict MVP):**
   - **UI (View):** Only widgets, signals, and set/get methods. Place views in `presentation/modules/<module>/views/` and name them `*_widget.py`.
   - **Presenter:** All UI business logic. Place presenters in `presentation/modules/<module>/presenters/` and name them `*_presenter.py`.
   - **Services:** Calculations and business rules in `application/services/`.
   - **DTOs:** Data transfer objects between layers in `application/dtos/`.
   - **Managers:** Cross-cutting features (themes, currency, prefs, PDF) in `core/managers/`.
   - **Repositories:** SQLite access in `infrastructure/database/repositories/` (never from the UI).
   - **Domain:** Entities and enums in `domain/models/` and `domain/enums/`.
   - **Facade:** Service orchestration in `application/facades/voxeprint_facade.py`.
   - **Key rules:**
     - Views MUST NOT access repositories or services directly.
     - Presenters MUST NOT import from `infrastructure/` directly; use the facade or managers.
     - Repositories MUST NOT know about DTOs or the UI.
5. **Do not use `print()`.** Always use `VoxeprintLogger` for logs.
6. **Do not add unrequested features.**
7. **Do not comment or document code you did not modify.**
8. **Follow UI conventions:**
   - Fields are always disabled by default; enable only when editing.
   - Use `CurrencyAwareLabel` for dynamic currency labels (`{symbol}`).
   - Do not hardcode colors except for specific cases.
   - All UI texts in Spanish and prepare `LABELS = {}` dictionaries for future i18n.
9. **Internationalization:**
   - All texts in Spanish
   - Use `LABELS = {}` dictionaries in views to facilitate future migration
10. **Update or create tests if applicable.**

---

## Pull Request Process

1. **Always make your changes on `develop`.**
2. **Clearly describe your change** in the PR (what problem it solves, how to test it).
3. **Link the PR to an issue or task** if applicable.
4. **Do not mix refactors with features.**
5. **Pass all automatic checks** (lint, tests, etc.).
6. **Request review from a maintainer.**

---

## Code Style

- Python 3.10+
- Use static typing where possible
- Follow PEP8
- Do not leave dead code or TODOs without an associated issue

---

## Contact

For questions, suggestions or reports, open an issue or contact the maintainers.

Thank you for helping improve Voxeprint!
