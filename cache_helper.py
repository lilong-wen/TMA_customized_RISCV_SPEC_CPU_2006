"""
Helper functions for creating different levels of cache configurations
without explicit parent parameters.
"""

def create_cache_config(size, assoc, tag_latency, data_latency, 
                       response_latency, mshrs, tgts_per_mshr):
    """Create a general cache configuration dictionary"""
    return {
        'size': size,
        'assoc': assoc,
        'tag_latency': tag_latency,
        'data_latency': data_latency,
        'response_latency': response_latency,
        'mshrs': mshrs,
        'tgts_per_mshr': tgts_per_mshr
    }

def create_l1_cache_config(size="32kB", assoc=8):
    """Create a L1 cache configuration"""
    return create_cache_config(
        size=size,
        assoc=assoc,
        tag_latency=1,
        data_latency=1,
        response_latency=1,
        mshrs=16,
        tgts_per_mshr=8
    )

def create_l2_cache_config(size="256kB", assoc=8):
    """Create a L2 cache configuration"""
    return create_cache_config(
        size=size,
        assoc=assoc,
        tag_latency=10,
        data_latency=10,
        response_latency=5,
        mshrs=32,
        tgts_per_mshr=8
    )

def create_l3_cache_config(size="2MiB", assoc=16):
    """Create a L3 cache configuration"""
    return create_cache_config(
        size=size,
        assoc=assoc,
        tag_latency=20,
        data_latency=20,
        response_latency=10,
        mshrs=64,
        tgts_per_mshr=16
    )

def create_l1_cache(size="32kB"):
    """Create a L1 cache object"""
    from m5.objects import Cache
    return Cache(**create_l1_cache_config(size))

def create_l2_cache(size="256kB"):
    """Create a L2 cache object"""
    from m5.objects import Cache
    return Cache(**create_l2_cache_config(size))

def create_l3_cache(size="2MiB", assoc=16):
    """Create a L3 cache object"""
    from m5.objects import Cache
    return Cache(**create_l3_cache_config(size, assoc))
    
def create_cache(**params):
    """Create a cache with the provided parameters"""
    from m5.objects import Cache
    return Cache(**params)
