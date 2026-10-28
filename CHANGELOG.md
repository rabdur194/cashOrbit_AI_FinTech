# Changelog

## Complete organized package
- Consolidated the app, bKash/SSLCOMMERZ sandbox adapter code, environment examples, Docker configuration, CI workflow, and backend migration files in one project root.
- Added an organized documentation set: index, getting started, feature matrix, API guide, data model, testing, troubleshooting, learning guide, payment setup, architecture, AWS deployment, product workflows, and roadmap.
- Added root-level security and contribution guidance.
- Removed Python bytecode and pytest cache artifacts from the distributable archive.
- Clarified sandbox/production boundaries and verification steps throughout the docs.


## AI architecture upgrade
- Split the large frontend page into domain-specific React component files and shared TypeScript types.
- Added the read-only AI Finance Operations Assistant, optional OpenAI-compatible API integration, organization-scoped invoice context, demo fallback, and assistant-specific UI styles.
- Added `OPENAI_API_KEY` and `OPENAI_MODEL` environment settings.
