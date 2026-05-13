# DevLog Global Configuration

## Basic Settings

- **Root Directory**: `D:\Projects\my-devlog`
- **Symbol Set**: `unicode`
- **Language**: `zh`
- **Default Project**: None
- **User**: `ytzhao`

## Symbol Scheme Mapping

When `symbol-set: unicode`:
- Note: `·`
- Problem: `×`
- Learning: `-`
- Idea: `!`
- Todo: `○`
- Done: `✓`
- Migrate: `→`

## AI Tool Guidelines

- Read this file to get the root directory path, do not hardcode
- Use the symbol scheme specified above consistently
- Tag format: `@ProjectName` (do NOT use `#ProjectName` to avoid Markdown header conflict)
- AI only writes to `daily/` and `inbox.md`, do NOT write to `projects/` directly
