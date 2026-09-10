# Imported 2015 winner-list test sources

Tests generate synthetic records with the five source schemas to exercise
Unicode filenames, leading zeros, quoted fields, repeated rows, invalid input,
missing names, and contested/unopposed semantics. Phone numbers are omitted
from derived tables. All other source fields are retained, with empty cells
represented as null.

The complete-data test checks all 226 files in
`data/raw/2015/winner_lists/SOURCE_MANIFEST.json` against their original byte
hashes and verifies every retained field in the five derived Parquet files.
Source: <http://sec.up.nic.in/ElecLive/WinnerList.aspx>.
Original capture times are unknown; the manifest pins the source repository
and original collection commit. Tests make no source-site requests.
