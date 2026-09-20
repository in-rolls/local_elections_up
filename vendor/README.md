# Shared decoder build dependency

The wheel contains the shared research code built from central commit `bf536affd015aba5820379ad99f0b6d24780e19b`. It is a build dependency, not a data release. Its upstream MIT license is included inside the wheel.

[The provenance receipt](../data/catalogs/shared_decoder.json) records the source repository, exact commit, build command, wheel hash, and decoder hash. `uv.lock` pins the wheel bytes. A relative wheel source makes checkout builds independent of the central repository's large data history and of archive-download availability.
