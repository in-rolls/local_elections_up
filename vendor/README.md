# Shared decoder build dependency

The wheel contains the shared research code built from central commit `d48524744a0d39fc167355c6be066fa7ab2b7ce4`. It is the `local-elections` 0.7.0 package, a build dependency, not a data release. Its decoder is the one that produced the released office labels (`decoder_source_sha256` in `data/release/offices/manifest.json`). Its upstream MIT license is included inside the wheel.

[The provenance receipt](../data/catalogs/shared_decoder.json) records the source repository, exact commit, build command, wheel hash, and decoder hash. `uv.lock` pins the wheel bytes. A relative wheel source makes checkout builds independent of the central repository's large data history and of archive-download availability.
