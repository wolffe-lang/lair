# Toolchain pin prediction

The release pair and its bundled standard library should build the engine without changing its behaviour. The formatter and checked tests should pass; both compiled tiers should build, and the sound, input and selftest rows should give the same answers. A refusal by the new compiler will be recorded and addressed separately from the pin move.

The baseline runs against the existing pinned toolchain before the move. The same checks run against the new pins at the final head. A deliberate independent break must make its named row fail before the final green take.
