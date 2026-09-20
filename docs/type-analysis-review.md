# Typed-container diagnostic review

Technical investigation on 2026-09-20, without application-source changes,
annotation removal, diagnostic filtering, or upstream implementation changes.
This review does not represent Maintainer approval.

## Runtime and probes

Runtime: combined WFL `df6ad9a2f9f401d943edfdec2e3804941a9c513f`, reporting 26.9.12,
SHA-256 `b96c06f6013a9a64d4d042c9b379a30af1c8d274d7855b5ebe9d7fe14a750d1c`.
The eight minimal WFL probes and captured output remain under ignored
`target/type-analysis-probes/`. Each executable probe was run as:

```text
target/runtime/combined-df6ad9a2/wfl.exe --test target/type-analysis-probes/<name>.test.wfl
```

All eight execution tests passed, one assertion case per probe. These are
runtime characterization results, not a claim of clean static analysis.
Their `.test.wfl.log` files retain every diagnostic.

| Probe | Static diagnostic | Interpretation |
|---|---|---|
| `list-parameter` | `List` differs from `List of Any`; a list argument also differs from `List`. | Inconsistent parser representation of the same collection annotation. |
| `container-parameter` | Cannot access `label` on non-container type `Item`. | Named container parameter is represented as a custom type, but the property resolver does not recognize that registered container. |
| `include-definition` | Included container type/metadata not found. | Static include traversal is absent; the definition exists when execution reaches it. |
| `parent-definition` | Container metadata not found in an included consumer. | Parent type symbols alone do not populate the analyzer's container registry. |
| `parent-after-call` | Container metadata not found after a parent action call. | Same metadata limitation; no runtime failure. |
| `parent-after-method` | Expected `Container<ParentItem>` but found `Any`. | Conservative call effects widen a parent container binding seeded as mutable, even though this particular method leaves it intact. |
| `untyped-factory` | Typed `Text` property initialized from `Unknown`. | Intentional persistent-property safety diagnostic: the untyped function signature does not establish its input contract. |
| `typed-factory` | None. | Adding the existing `as text` parameter annotation establishes the contract and preserves the same successful call. |

The final two files differ only by `with parameters label_value` versus
`with parameters label_value as text`. This distinguishes an authored static
contract gap from a runtime false positive. Successful tests alone cannot prove
that every untyped call will always satisfy a typed property.

## Concrete causes and source anchors

Source references below are in `WebFirstLanguage/wfl` at the revision above.

1. `src/parser/stmt/containers.rs:64` parses a bare property `List` as
   `Type::List(Type::Any)`. In contrast, method parameter parsing at
   `src/parser/stmt/actions.rs:541` uses `colon_type_from_token` at line 45,
   whose primitive cases omit `List`, leaving `Type::Custom("List")`.
   Scriptorium uses the documented colon-style method form, not an invented
   annotation syntax. A minimal reproduction is:

   ```wfl
   create container Basket:
       property entries: List defaults []
       action replace_entries needs replacement: List:
           change entries to replacement
       end
   end
   ```

2. `src/typechecker/mod.rs:10693` resolves dot-property access for
   `ContainerInstance` and other concrete runtime types. A method parameter
   annotated `incoming: Item` instead carries `Custom("Item")`. That custom
   name is valid for nominal assignment compatibility
   (`src/typechecker/mod.rs:11107`), but does not reach the registered
   container's property lookup. The minimal failing diagnostic is produced by
   `change saved_label to incoming.label` in a method with `incoming: Item`,
   even when `Item` and its `Text` property are in the same file.

3. `src/typechecker/mod.rs:7631` explicitly documents that the checker does
   not parse includes. The runtime checks each included file before executing
   its nested includes (`src/interpreter/mod.rs:9190` and `:9219`).
   `snapshot_parent_scope` (`src/interpreter/mod.rs:5292`) transports variable
   types and action signatures, but not the container metadata registry.
   Consequently a later file can see `Container("Item")` without its field and
   inheritance metadata. `escape_all_visible_mutable_state`
   (`src/typechecker/mod.rs:1786`) further widens mutable imported bindings to
   `Any` across an opaque method/constructor call; the local-container
   declaration is registered immutable while the runtime snapshot uses the
   runtime binding's mutability. The `parent-after-method` probe reproduces
   exactly the application's `not a container type ... found Any` category.

4. `are_declared_property_types_compatible`
   (`src/typechecker/mod.rs:10975`) deliberately rejects `Any`/`Unknown`
   sources for a concrete persistent property. Ordinary action compatibility
   is more gradual; persistent properties retain their declared type on later
   reads, so accepting an unchecked replacement would make those reads
   unsound. Existing Rust regression coverage at
   `tests/typechecker_container_contract_test.rs:177` specifically protects
   this rule. Do not loosen it to silence Scriptorium factories. Where a
   factory's parameter contract is known, adding the existing specific type
   annotation is the appropriate application improvement. Dynamic list
   construction and included action return inference may still need a separate
   evidence-based checker improvement; assigning `Any` everywhere is not one.

The container guide demonstrates colon-style properties, `needs` parameters,
and named container parameters (`docs/04-advanced-features/containers-oop.md`,
including its Task/TaskList example). The action guide documents the additive
`as text` form (`docs/03-language-basics/actions-functions.md:249`).
The CLI deliberately emits type diagnostics as nonfatal warnings before normal
execution (`src/main.rs:965`); the included-file path does the same. The
`error[ERROR]` presentation does not mean these tests were skipped or that the
runner discarded a nonzero result. It also does not make the diagnostic
limitations disappear.

## Bounded follow-up plan

The first two issues are suitable for a focused upstream change, separately
reviewed and tested before use:

- Normalize the already documented bare `List` method-parameter annotation to
  the same list type as a property. Reuse the property type grammar if extending
  parameter annotations to nested lists, rather than maintaining divergent
  parsers. Preserve existing case and custom-type rules; explicitly examine
  legacy containers named `List` before changing their interpretation.
- Resolve `Custom(name)` through the registered container in value-member
  contexts. Reuse inheritance/property lookup, preserve built-in handle and
  temporal type rules, and continue rejecting unknown names and missing fields.
  Check method calls through the same nominal value annotations as well.
- Use a WFL process driver to run minimal WFL fixtures and inspect captured
  diagnostics. Positive fixtures must still execute and lose only the false
  diagnostic; negative fixtures must retain mismatched element/property types,
  missing fields, unrelated container arguments, and unsafe `Any`/`Unknown`
  persistent-property assignments. Cover inherited named parameters and
  unchanged built-in/custom name behavior. Register these WFL tests in the
  existing gated runner; no new Rust/Python test scenario or driver is needed.

Include-aware analysis is a larger change: preserving complete parent container
contracts is only part of it, because a main file is checked before a nested
include executes. A sound static dependency pass must respect include scope,
shadowing, inheritance, cycles, source budgets, and runtime binding effects
without executing application code. Flattening the application's include tree,
reordering definitions to fool the checker, marking unknown definitions as
containers, or broadly exempting `Any` are not sound small patches.

These findings are not new functional prerequisites for the passing CMS flows.
They are real diagnostic limitations and authored contract gaps to track
explicitly; the application must not claim a clean type-analysis run. No new
upstream PR was started as part of this investigation.

## No-Unlearning assessment

The foundation's overarching invariant (`docs/wfl-foundation.md:101`) requires
beginner and production forms to be the same or joined by an additive path.
Making `List` and named-container annotations mean the same thing on properties
and parameters repairs that path. Adding a precise parameter annotation to a
known factory contract also follows it: the existing call form and property
model stay intact. Removing annotations, teaching different spellings merely
to evade diagnostics, flattening reusable modules, or asking authors to ignore
all type warnings would create habits that production users must unlearn.
Keeping the current limitations visible is an honest interim statement, not a
foundation exception or acceptance of those workarounds.
