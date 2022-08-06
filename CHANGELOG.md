# Pynalyser Changelog

## 0.2.0 (???)

### Added
- `analysers.pipeline.py`
- `symbol.MultiDefSymbol` and relevant analyser - `RedefinitionAnalyser`
- `AnalysisContext.unpack()`
- `inherit_dicts.py` with `InheritDicts`
- Support of python 3.10 (at least partially)
- The first version of the documentation!
- `report` parameter to the deref()

### Changed
- Finally `global` and `nonlocal` are now analyzed in `ScopeAnalyser` instead of `Translator`
- `NodeVisitor.start` now don't take the second argument
- Move `symbol_table` from `Scope` and to be a separate structure in the `AnalysisContext`
- Move `return_type` from `Function` to `FunctionType`
- Moved `analysis.symbols.py` to `symbol.py`
- Renamed `SymbolData` to `Symbol` and `SymTabType` to `SymbolTableType`
- `analysis.X_types.py` are all moved in `types\`
- `normalize_ast.py` and `portable_ast.py` are moved into `ast` submodule
- filename is now optional for `parse_string` and `parse_ast`

### Removed
- "Graph Visit Casher"
- `ScopeReference` `ScopeDefs` from `acr.classes`
- `symbols.SymbolTable`
- `main.analyse_context` and `main.analyse`
- Support of python 3.6

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
