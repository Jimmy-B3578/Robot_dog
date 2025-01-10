def filter_value(new_val, old_val):
    """
    Equivalent to:
      long filter(long lengthOrig, long currentValue) {
        int filter = 15;
        long lengthFiltered =  (lengthOrig + (currentValue * filter)) / (filter + 1);
        return lengthFiltered;
      }
    """
    FILTER = 15
    # new_val  => lengthOrig
    # old_val  => currentValue
    return (new_val + (old_val * FILTER)) / (FILTER + 1)
