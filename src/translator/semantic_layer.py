"""Semantic post-processor for translated C# — rewrites patterns that compile but don't run in Unity.

The AST translator handles syntax (Python -> C#) but not semantics (simulator -> Unity patterns).
This module applies regex-based rewrites to strip simulator artifacts and fix Unity-incompatible
constructs in the translated output.

Usage:
    from src.translator.semantic_layer import transform

    clean_cs = transform(raw_cs_code)
"""

from __future__ import annotations

import re


# C# value types whose nullable form (int?, float?, etc.) is intentional
_VALUE_TYPES = frozenset({
    "int", "float", "double", "bool", "byte", "sbyte",
    "short", "ushort", "uint", "long", "ulong", "decimal",
    "char", "Vector2", "Vector3", "Vector4", "Quaternion",
    "Color", "Color32", "Rect", "Bounds",
})


def transform(
    cs_source: str,
    *,
    singletons: set[str] | None = None,
    current_classes: set[str] | None = None,
) -> str:
    """Apply semantic rewrites to translated C#.

    Processes the C# source in priority order:
    1. Strip simulator-only code (pygame, pymunk, simulator managers)
    2. Rewrite Python type hints that leaked through translation
    3. Annotate constructor patterns
    4. Annotate singleton patterns
    5. Rewrite cross-class singleton access to SerializeField reference (S2-3)

    Args:
        cs_source: Translated C# code.
        singletons: Set of class names that are singletons (detected at project level).
        current_classes: Set of class names defined in this file (skip self-rewrites).
    """
    if not cs_source:
        return cs_source

    cs_source = _strip_simulator_code(cs_source)
    cs_source = _strip_ambiguous_usings(cs_source)
    cs_source = _rewrite_type_hints(cs_source)
    cs_source = _annotate_constructors(cs_source)
    cs_source = _assign_default_ui_font(cs_source)
    cs_source = _annotate_singletons(cs_source)
    if singletons:
        cs_source = rewrite_singleton_access(
            cs_source,
            singletons=singletons,
            current_classes=current_classes or set(),
        )
    cs_source = _fix_bare_try_blocks(cs_source)
    cs_source = _hoist_branch_locals(cs_source)
    cs_source = _clean_redundant_conditions(cs_source)
    cs_source = _clean_empty_lines(cs_source)

    return cs_source


def rewrite_singleton_access(
    cs_source: str,
    *,
    singletons: set[str],
    current_classes: set[str],
) -> str:
    """Rewrite `Singleton.Instance.X` to `singleton.X` via [SerializeField] reference.

    For each singleton class ``S`` that is referenced as ``S.Instance.X`` in this
    file, and where ``S`` is NOT itself defined in this file, inject
    ``[SerializeField] private S sCamel;`` into each consuming class and rewrite
    the call sites to use the field.

    Skips the singleton's own file so `S` can still access `S.Instance` internally
    (used for singleton initialization and Reset patterns).
    """
    # Find which singletons this file *consumes* (and doesn't itself define)
    consumed: set[str] = set()
    for s in singletons:
        if s in current_classes:
            continue
        # Match `S.Instance.` with word-boundary on S to avoid prefix collisions
        if re.search(rf'\b{re.escape(s)}\.Instance\b', cs_source):
            consumed.add(s)

    if not consumed:
        return cs_source

    # Parse classes in the file (lightweight: regex on `public class Name`)
    class_spans = _find_class_spans(cs_source)
    if not class_spans:
        return cs_source

    # Build per-class plan: (brace_pos, end_pos, [(singleton, field_name, inject?)])
    # Process spans from last→first so position-based edits don't invalidate earlier ones.
    class_spans.sort(key=lambda sp: -sp[1])  # sort by brace_pos desc

    # Track which class got which self-wire fields so we can inject a
    # matching Awake() fallback after the rewrite pass.  Without this,
    # every [SerializeField] we inject here becomes a null ref at runtime
    # unless something external wires it (which the CoPlay generator
    # currently doesn't do for cross-MonoBehaviour refs).  See
    # data/lessons/flappy_bird_deploy.md gap 2.
    per_class_fallbacks: dict[str, list[tuple[str, str]]] = {}

    for cls_name, brace_pos, end_pos in class_spans:
        body = cs_source[brace_pos + 1:end_pos]
        body_changed = False
        injections: list[str] = []
        fallbacks: list[tuple[str, str]] = []  # (SingletonType, fieldName)

        for s in consumed:
            if not re.search(rf'\b{re.escape(s)}\.Instance\b', body):
                continue
            # Default field name from class name; reuse existing [SerializeField] name if present
            field_name = s[0].lower() + s[1:]
            existing = re.search(
                rf'\[SerializeField\]\s+private\s+{re.escape(s)}\s+(\w+)\s*;',
                body,
            )
            if existing:
                field_name = existing.group(1)
            else:
                injections.append(f"\n    [SerializeField] private {s} {field_name};")

            # Rewrite S.Instance → field_name inside this class body only
            body = re.sub(
                rf'\b{re.escape(s)}\.Instance\b',
                field_name,
                body,
            )
            body_changed = True
            fallbacks.append((s, field_name))

        if body_changed or injections:
            new_body = "".join(injections) + body
            cs_source = cs_source[:brace_pos + 1] + new_body + cs_source[end_pos:]
        if fallbacks:
            per_class_fallbacks.setdefault(cls_name, []).extend(fallbacks)

    # Second pass: inject Awake() self-wire lines so consumers work at
    # runtime without Inspector wiring.  If the class already has an
    # Awake(), prepend the fallback lines; otherwise create one.
    for cls_name, fallbacks in per_class_fallbacks.items():
        cs_source = _inject_awake_fallback(cs_source, cls_name, fallbacks)

    return cs_source


def _inject_awake_fallback(
    cs_source: str,
    class_name: str,
    fallbacks: list[tuple[str, str]],
) -> str:
    """Prepend `if (field == null) field = Type.Instance;` self-wire lines
    into ``class_name``'s Awake, or create an Awake() if none exists.

    Ensures scripts whose singleton SerializeField refs weren't wired in
    the Inspector still work at runtime via the singleton fallback.
    """
    spans = _find_class_spans(cs_source)
    for name, brace_pos, end_pos in spans:
        if name != class_name:
            continue
        body = cs_source[brace_pos + 1:end_pos]
        awake_lines = [
            f"        if ({field_name} == null) {field_name} = FindObjectOfType<{singleton}>();"
            for singleton, field_name in fallbacks
        ]
        awake_block = "\n".join(awake_lines)

        awake_match = re.search(r'void\s+Awake\s*\(\s*\)\s*\{', body)
        if awake_match:
            insert = awake_match.end()
            new_body = body[:insert] + "\n" + awake_block + body[insert:]
        else:
            new_body = body.rstrip() + (
                "\n\n    void Awake()\n    {\n" + awake_block + "\n    }\n"
            )
        return cs_source[:brace_pos + 1] + new_body + cs_source[end_pos:]
    return cs_source


def _find_class_spans(cs_source: str) -> list[tuple[str, int, int]]:
    """Find `public class Name ... { ... }` spans in cs_source.

    Returns list of (class_name, opening_brace_index, closing_brace_index).
    Uses brace-depth matching. Skips nested types.
    """
    spans: list[tuple[str, int, int]] = []
    for m in re.finditer(r'public\s+(?:abstract\s+|sealed\s+|static\s+)?class\s+(\w+)[^{]*\{',
                         cs_source):
        cls_name = m.group(1)
        brace_pos = m.end() - 1  # position of the `{`
        # Find matching `}` by brace depth
        depth = 1
        i = brace_pos + 1
        while i < len(cs_source) and depth > 0:
            ch = cs_source[i]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
            i += 1
        if depth == 0:
            spans.append((cls_name, brace_pos, i - 1))
    return spans


def _strip_ambiguous_usings(cs: str) -> str:
    """Strip 'using System;' to avoid CS0104 ambiguity with UnityEngine types (e.g. Random).

    Unity code rarely needs bare System — Mathf covers math, and specific
    System.* imports (System.Linq, System.Collections) are kept as-is.
    """
    cs = re.sub(r'^using System;\n', '', cs, count=1, flags=re.MULTILINE)
    return cs


def _strip_simulator_code(cs: str) -> str:
    """Priority 1: Remove pygame, pymunk, and simulator manager references."""

    # --- pygame references ---
    # Replace pygame.Surface type with Sprite
    cs = re.sub(r'pygame\.Surface\??\s*\[\]', 'Sprite[]', cs)
    cs = re.sub(r'pygame\.Surface\??', 'Sprite', cs)

    # Strip entire lines containing pygame references (calls, init, etc.)
    cs = re.sub(r'[^\n]*\bpygame\b[^\n]*\n?', '', cs)

    # --- pymunk references ---
    cs = re.sub(r'[^\n]*\bpymunk\b[^\n]*\n?', '', cs)

    # --- Simulator managers ---
    cs = re.sub(r'[^\n]*\bLifecycleManager\b[^\n]*\n?', '', cs)
    cs = re.sub(r'[^\n]*\bPhysicsManager\b[^\n]*\n?', '', cs)
    cs = re.sub(r'[^\n]*\bDisplayManager\b[^\n]*\n?', '', cs)

    # Strip variable stubs left behind by manager stripping (e.g., lm.Something())
    cs = re.sub(r'\s*var lm = [^;]*;\n?', '', cs)
    cs = re.sub(r'[^\n]*\blm\.[^\n]*\n?', '', cs)
    cs = re.sub(r'\s*var pm = [^;]*;\n?', '', cs)
    cs = re.sub(r'[^\n]*\bpm\.[^\n]*\n?', '', cs)
    cs = re.sub(r'\s*var dm = [^;]*;\n?', '', cs)
    cs = re.sub(r'[^\n]*\bdm\.[^\n]*\n?', '', cs)

    # --- Python stdlib filesystem references ---
    cs = re.sub(r'[^\n]*\bos\.path\b[^\n]*\n?', '', cs)
    cs = re.sub(r'[^\n]*\b__file__\b[^\n]*\n?', '', cs)

    # S12-4: After pygame stripping, functions like load_sprite_file often
    # end with `return surf;` where `surf` was the stripped pygame.Surface
    # local. Replace with `return default;` so the method compiles. The actual
    # sprite loading will be handled manually in Unity (e.g. Resources.Load<Sprite>).
    cs = re.sub(
        r'(\breturn\s+)(?:surf|image|sound|tex|texture)\s*;',
        r'\1default;',
        cs,
    )

    # --- app.run() ---
    cs = re.sub(r'[^\n]*\bapp\.run\s*\([^)]*\)\s*;[^\n]*\n?', '', cs)

    return cs


def _rewrite_type_hints(cs: str) -> str:
    """Priority 2: Fix Python type annotations that leaked into C#."""

    # Strip nullable ? on reference types (not value types)
    # Match: public TypeName? fieldName  or  private TypeName? fieldName
    # But preserve int?, float?, Vector3?, etc.
    def _strip_nullable_ref(m: re.Match) -> str:
        prefix = m.group(1)   # visibility + optional modifiers
        type_name = m.group(2)  # the type
        suffix = m.group(3)     # field name + rest
        if type_name in _VALUE_TYPES:
            return m.group(0)  # keep as-is
        return f"{prefix}{type_name} {suffix}"

    cs = re.sub(
        r'((?:public|private|protected)\s+(?:static\s+)?(?:readonly\s+)?)(\w+)\?\s+(\w+)',
        _strip_nullable_ref,
        cs,
    )

    # Also strip standalone ClassName? in return types and local vars
    # e.g., GameManager? in "return GameManager.Instance;"
    # This is handled by the field pattern above for declarations

    # Rewrite !in operator: "if (item !in collection)" -> "if (!collection.Contains(item))"
    cs = re.sub(
        r'if\s*\(\s*(\w+)\s+!in\s+(\w+)\s*\)',
        r'if (!\2.Contains(\1))',
        cs,
    )

    return cs


def _annotate_constructors(cs: str) -> str:
    """Priority 3: Make `new GameObject("Name")` idempotent (S7-5) and annotate
    dynamic calls with a TODO.

    In the breakout debug session (2026-04-13), translated ``SetupUi()`` was
    calling ``new GameObject("UICanvas")`` and duplicating a UICanvas that
    already existed in the scene, producing a NullRef when the duplicates had
    no parented Text components. The fix is to rewrite string-literal
    constructors to a find-or-create pattern so the method becomes idempotent.
    """

    # 1. Rewrite `new GameObject("LiteralName")` → `(GameObject.Find("LiteralName") ?? new GameObject("LiteralName"))`
    #    Only applies when the argument is a single string literal (deterministic).
    def _idempotent_replace(m: re.Match) -> str:
        name_literal = m.group(1)
        return f'(GameObject.Find({name_literal}) ?? new GameObject({name_literal}))'

    cs = re.sub(
        r'new\s+GameObject\s*\(\s*("[^"\n]+")\s*\)',
        _idempotent_replace,
        cs,
    )

    # 2. For any remaining dynamic `new GameObject(...)` calls (non-literal
    #    argument — e.g., variable or expression), keep the TODO comment.
    def _add_constructor_comment(m: re.Match) -> str:
        line = m.group(0)
        comment = " // TODO: wire via Inspector or Instantiate"
        if "// TODO:" in line:
            return line
        return line.rstrip() + comment

    cs = re.sub(
        r'[^\n]*new\s+GameObject\s*\([^\n]*',
        _add_constructor_comment,
        cs,
    )

    return cs


def _assign_default_ui_font(cs: str) -> str:
    """Inject a default font after each `.AddComponent<Text>()` call (S7-5).

    Unity UI.Text renders nothing when ``font`` is null — and calling
    ``text.text = "..."`` on a Text with no font throws NullReferenceException.
    This pass inserts a fallback ``Resources.GetBuiltinResource<Font>(...)``
    assignment immediately after Text component creation so translated UI
    setup code works without manual font wiring.
    """
    # Match assignments like:
    #   X = Y.AddComponent<Text>();
    # and append a font default on the next line with matching indentation.
    def _inject_font(m: re.Match) -> str:
        indent = m.group(1)
        full = m.group(0)
        target = m.group(2)  # assignment target (e.g., ScoreText, inst.ScoreText)
        follow = (
            f'\n{indent}if ({target} != null && {target}.font == null) '
            f'{target}.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");'
        )
        return full + follow

    cs = re.sub(
        r'(^[ \t]*)([\w.]+)\s*=\s*\w+\.AddComponent<Text>\(\)\s*;',
        _inject_font,
        cs,
        flags=re.MULTILINE,
    )
    return cs


def _annotate_singletons(cs: str) -> str:
    """Priority 4: Detect and annotate singleton pattern.

    Also renames 'instance' to 'Instance' (Unity convention for singleton properties).
    """

    # Match: public static ClassName instance (with or without assignment)
    def _add_singleton_comment(m: re.Match) -> str:
        line = m.group(0)
        comment = "// Singleton \u2014 wire via Inspector [SerializeField] on dependents"
        if "Singleton" in line:
            return line
        return f"    {comment}\n{line}"

    cs = re.sub(
        r'^(\s*public\s+static\s+\w+\s+instance\b[^\n]*)',
        _add_singleton_comment,
        cs,
        flags=re.MULTILINE,
    )

    # Rename 'instance' to 'Instance' for static singleton fields and all references
    # Static field declaration: public static GameManager instance → Instance
    cs = re.sub(
        r'(public\s+static\s+\w+\s+)instance\b',
        r'\1Instance',
        cs,
    )
    # References: ClassName.instance → ClassName.Instance
    cs = re.sub(r'(\w+)\.instance\b', r'\1.Instance', cs)

    return cs


def _fix_bare_try_blocks(cs: str) -> str:
    """Remove `try { ... }` blocks that aren't followed by catch/finally (S11-2).

    After pygame-stripping, a Python `try: pygame.X(); except: pass` can leave
    behind `try { /* pass */ }` with no catch — a C# compile error. If the try
    body is effectively empty (pass or whitespace), drop the whole try block.
    Otherwise, fold the body out (run it unconditionally) since Unity's codepath
    usually shouldn't fail here anyway.
    """
    lines = cs.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        # Detect `try` keyword at line-start (possibly indented)
        if re.match(r"^\s*try\s*$", line) and i + 1 < n and lines[i + 1].strip() == "{":
            # Find matching }
            depth = 0
            j = i + 1
            end_try = -1
            while j < n:
                for ch in lines[j]:
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            end_try = j
                            break
                if end_try != -1:
                    break
                j += 1
            # Look ahead for catch/finally
            k = end_try + 1 if end_try != -1 else i + 1
            while k < n and lines[k].strip() == "":
                k += 1
            has_handler = k < n and re.match(r"^\s*(catch|finally)\b", lines[k])
            if end_try != -1 and not has_handler:
                # Determine if body is effectively empty
                body = lines[i + 2:end_try]
                nonempty = [ln for ln in body
                            if ln.strip() and ln.strip() != "/* pass */"]
                if not nonempty:
                    # Drop the whole try block
                    i = end_try + 1
                    continue
                # Fold body out — keep the statements, drop try/braces
                out.extend(body)
                i = end_try + 1
                continue
        out.append(line)
        i += 1
    return "\n".join(out)


def _hoist_branch_locals(cs: str) -> str:
    """Hoist variables that get typed-declared in an if-branch but reused in
    a sibling else-branch or after the if-block (S10-4, pacman_v2 movement.cs).

    Python pattern:
        if cond:
            snapped = ...
        else:
            snapped = ...
        use(snapped)   # out of scope in C# if declared inside if-block

    Rewrite:  `Type VAR = NEW;` inside an if-block  →  `VAR = NEW;`
    when the same bare `VAR = ...` appears in a sibling else-branch. Insert
    a `Type VAR = default;` hoist before the if-block.

    Targets only the specific pattern where a typed declaration inside `if`
    is paired with a bare assignment inside the matching `else`; does not
    touch single-branch declarations.
    """
    # Match:  if (...) { ... Type VAR = EXPR; ... } else { ... VAR = EXPR2; ... }
    # Use a line-oriented scan — full C# block parsing is too heavy for regex.
    lines = cs.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        # Detect an `if (...)` line; then the following line should be `{`
        if re.match(r"\s*if\s*\(", line) and i + 1 < n and lines[i + 1].strip() == "{":
            # Find matching closing brace
            depth = 0
            j = i + 1
            end_if = -1
            while j < n:
                for ch in lines[j]:
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            end_if = j
                            break
                if end_if != -1:
                    break
                j += 1
            if end_if == -1 or end_if + 1 >= n:
                out.append(line)
                i += 1
                continue
            # Check next non-whitespace line for `else`
            k = end_if + 1
            while k < n and lines[k].strip() == "":
                k += 1
            if k >= n or not re.match(r"\s*else\b", lines[k]):
                out.append(line)
                i += 1
                continue
            # Find else-block end
            if k + 1 >= n or lines[k + 1].strip() != "{":
                out.append(line)
                i += 1
                continue
            depth = 0
            m = k + 1
            end_else = -1
            while m < n:
                for ch in lines[m]:
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            end_else = m
                            break
                if end_else != -1:
                    break
                m += 1
            if end_else == -1:
                out.append(line)
                i += 1
                continue
            # Scan if-body for typed declarations and else-body for bare re-assignments
            if_body = lines[i + 2:end_if]
            else_body = lines[k + 2:end_else]
            decl_re = re.compile(r"^(\s*)(\w+(?:<[^>]+>)?(?:\[\])?)\s+(\w+)\s*=\s*([^;]+);\s*$")
            hoists: list[tuple[str, str, str]] = []  # (indent, type, name)
            new_if = list(if_body)
            for idx, ln in enumerate(if_body):
                m2 = decl_re.match(ln)
                if not m2:
                    continue
                indent, typ, name, rhs = m2.groups()
                if typ in ("var", "if", "else", "for", "while", "return"):
                    continue
                # Check else_body for bare assignment to same name
                bare_re = re.compile(rf"^\s*{re.escape(name)}\s*=")
                if any(bare_re.match(eb) for eb in else_body):
                    # Also check name isn't declared typed in else (nested scope OK)
                    if not any(re.match(rf"^\s*\w+(?:<[^>]+>)?(?:\[\])?\s+{re.escape(name)}\s*=", eb) for eb in else_body):
                        hoists.append((indent, typ, name))
                        new_if[idx] = f"{indent}{name} = {rhs};"

            if hoists:
                if_indent = re.match(r"^(\s*)", line).group(1)  # type: ignore
                for indent, typ, name in hoists:
                    out.append(f"{if_indent}{typ} {name} = default;")
                out.append(line)
                out.append(lines[i + 1])  # `{`
                out.extend(new_if)
                out.append(lines[end_if])  # `}`
                out.extend(lines[end_if + 1:end_else + 1])
                i = end_else + 1
                continue
        out.append(line)
        i += 1
    return "\n".join(out)


def _clean_redundant_conditions(cs: str) -> str:
    """Remove redundant condition fragments left by translation.

    - ``&& true`` and ``|| false`` are no-ops
    - ``true &&`` at the start of a condition is also a no-op
    - ``hasattr(...)`` translates to ``true`` — strip these artifacts
    """
    cs = re.sub(r'\s*&&\s*true\b', '', cs)
    cs = re.sub(r'\btrue\s*&&\s*', '', cs)
    cs = re.sub(r'\s*\|\|\s*false\b', '', cs)
    return cs


def _clean_empty_lines(cs: str) -> str:
    """Remove excessive blank lines left after stripping."""
    # Collapse 3+ consecutive blank lines to 2
    cs = re.sub(r'\n{4,}', '\n\n\n', cs)
    return cs
