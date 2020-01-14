# We first initialize the hash table where we will store all the (64-bit hash, C char array/pointer) couples.
cdef PreshMap hashmap = PreshMap(initial_size=1024)


cdef PreshCounter fast_count(list words):
    '''Count the number of occurrences of every word'''

    cdef:
        PreshCounter counter = PreshCounter(initial_size=256)
        bytes word

    for word in words:
        # Insert the word into the hash table, and increment the counter with
        # the 64-bit hash
        counter.inc(_insert_in_hashmap(word, len(word)), 1)

    return counter


cdef list text2bow(list words):
    '''Build the BoW representation of a list of words'''
    cdef:
        hash_t wordhash
        int i, freq
        list bow

    # First count the number of occurrences of every word
    counter = fast_count(words)

    # Convert the PreshCounter object to a more readable Python list `bow`,
    # for further usage
    bow = []
    for i in range(counter.c_map.length):
        wordhash = counter.c_map.cells[i].key
        if wordhash != 0:
            freq = <count_t>counter.c_map.cells[i].value
            # We use the 64-bit hashes instead of integer ids, which works
            # as well
            bow.append((wordhash, freq))

    return bow