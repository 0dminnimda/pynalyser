# Pynalyser Changelog

## 0.2.0 (???)

### Changed
- Finally `global` and `nonlocal` are now analyzed in `ScopeAnalyser` instead of `Translator`

### Removed
- "Graph Visit Casher"
- `acr.ScopeReference`

### Fixed
- `ACRCodeTransformer` now works properly
- Minor bugs

## 0.1.0 (2022-03-20)
### Added
- ACR (Abstract Code Representation) and tools for using it
- Extendable system for analysis
- Analysis of the scopes
- Partial type inference (and type system for it to work on)
- "Graph Visit Casher"
