# CLAUDE.md

Guidance for code assistants working in this repository.

## Annotation guidelines

The annotation guidelines exist in two versions that must always say the same thing:

- `docs/guidelines.md` — the full guide for human annotators (rationale, links, many examples).
- `docs/guidelines-llm.md` — a condensed version of the same rules for LLMs. The PDF-TEI-Editor's GROBID plugin points the "machine" annotation-rule refs of its documents at its sections, so the LLM Reviewer sends these instead of the full guide.

Rules:

- **Every change to one file must be mirrored in the other, in the same commit.** A new or changed rule, attribute value, element or example in `docs/guidelines.md` gets its condensed counterpart in `docs/guidelines-llm.md`, and vice versa. A change that only rewords the human guide's explanations without changing a rule needs no change in the LLM version, but still needs the sync step below.
- Each `##` section of `docs/guidelines-llm.md` condenses the `##` section of `docs/guidelines.md` with the same heading. Keep the headings identical, since the editor finds the sections by their heading anchors (`#citation-model` etc.). Renaming a heading also requires updating the URLs in the editor's GROBID plugin config (`annotation_guides.py` in mpilhlt/pte-plugins).
- After mirroring a change, run `python scripts/check-llm-digest.py --update` to record the new hashes, and `python scripts/check-llm-digest.py` to verify. CI runs the check and fails while a section changed on only one side.
- Style of `docs/guidelines-llm.md`: terse rules and tables, no rationale, no links, few and short examples. Keep every rule, element and attribute value. Write attribute values out one by one (`` `@type` is one of `court`, `legislature` ``), never as `type="a|b"`, which a model may copy literally.
