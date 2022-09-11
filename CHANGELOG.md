# Pynalyser Changelog


<!--

Template:

### Added
- for new features.

### Changed
- for changes in existing functionality.

### Deprecated
- for soon-to-be removed features.

### Removed
- for now removed features.

### Fixed
- for any bug fixes.

### Security
- in case of vulnerabilities.

-->


## 0.2.0 (???)

### Added
- `analysers.pipeline.py`
- `symbol.MultiDefSymbol` and relevant analyser - `RedefinitionAnalyser`
- `AnalysisContext.unpack()`
- `inherit_dicts.py` with `InheritDicts`
- Support of python 3.10 (at least partially)
- The first version of the documentation!
- `report` parameter to the deref()
- Basic reporting system
- `SingleType`: `is_type()` and `issubclass()`
- `Scope.enclosing` 🔼 Patched by `@groesie` in [#27](https://github.com/0dminnimda/pynalyser/pull/27)
- A new preferred way to collect names is `analysers.tools.collect_names()`
- `types.symbol_table_types.SymbolTableType.reset()`
- `types.symbol_table_types.Arg.iter()`
- Inheritance and MRO support for types

### Changed
- Finally `global` and `nonlocal` are now analyzed in `ScopeAnalyser` instead of `Translator`
- `NodeVisitor.start` now don't take the second argument
- Move `symbol_table` from `Scope` and to be a separate structure in the `AnalysisContext`
- Move `return_type` from `Function` to `FunctionType`
- Moved `analysis.symbols.py` to `symbol.py`
- Renamed `SymbolData` to `Symbol` and `SymTabType` to `SymbolTableType`
- `analysis.X_types.py` are all moved in `types\`
- `normalize_ast.py` and `portable_ast.py` are moved into `ast` submodule
- Filename is now optional for `parse_string` and `parse_ast`
- `CompareType` -> `CompareOpType`
- Implement accurate `BinOpType`, `CompareOpType` and `SubscriptType` `deref()`
- `analysers.redefinitions.RedefinitionAnalyser` -> `analysers.definitions.DefinitionAnalyser`
- Move parts of `analysers.scope.ScopeAnalyser` into `analysers.definitions.SymTabAnalyser`
- Update `analysers.pipeline.default_pipe`
- Move `UnionType.make()` functionality to `UnionType.deref()`
- Use `pyproject.toml` instead of `setup.py` 🔼 Patched by `@9gl` in [#15](https://github.com/0dminnimda/pynalyser/pull/15) and `@0dminnimda` in [#30](https://github.com/0dminnimda/pynalyser/pull/30)
- Move `mypy.ini` into `pyproject.toml`
- `PynalyserType.deref()` returns `SingleType`
- `SingleType` is renamed to `DataType`
- `is_type()` and `issubclass()` are moved to `types.inheritance`
- `issubclass()` renamed to `is_subclass()`

### Removed
- "Graph Visit Casher"
- `ScopeReference` `ScopeDefs` from `acr.classes`
- `symbols.SymbolTable`
- `main.analyse_context` and `main.analyse`
- Support of python 3.6
- `analysers.scope.SymTabAnalyser`
- `types.operations`

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

### Fixed
- `test_normalize_ast.py` 🔼 Patched by `@wert-rar` in [#3](https://github.com/0dminnimda/pynalyser/pull/3)
