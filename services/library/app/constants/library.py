from enum import StrEnum

from prepza_common.constants import DEFAULT_LANGUAGE


# How the public library can be ordered.
class LibrarySort(StrEnum):
    # Newest first.
    DATE = "date"
    # Best rated first, ratings weighed by how many there are (constants/feedback.py).
    RATING = "rating"
    # Most joined first.
    JOINERS = "joiners"


DEFAULT_LIBRARY_SORT = LibrarySort.RATING
# Shown besides the reader's own language by default: most public kits are in it.
LIBRARY_EXTRA_LANGUAGE = DEFAULT_LANGUAGE
