# Pynalyser Changelog

## 0.2.0 (???)

### Added
- `analysers.pipeline.py`
- `symbol.MultiDefSymbol` and relevant analyser - `RedefinitionAnalyser`
- `AnalysisContext.unpack()`

### Changed
- Finally `global` and `nonlocal` are now analyzed in `ScopeAnalyser` instead of `Translator`
- `NodeVisitor.start` now don't take the second argument
- Move `symbol_table` from `Scope` and to be a separate structure in the `AnalysisContext`
- Move `return_type` from `Function` to `FunctionType`
- Moved `analysis.symbols.py` to `symbol.py`
- Renamed `SymbolData` to `Symbol` and `SymTabType` to `SymbolTableType`
- `analysis.X_types.py` are all moved in `types\`

### Removed
- "Graph Visit Casher"
- `ScopeReference` `ScopeDefs` from `acr.classes`
- `symbols.SymbolTable`
- `main.analyse_context` and `main.analyse`

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
