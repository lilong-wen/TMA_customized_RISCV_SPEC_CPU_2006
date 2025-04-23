"""
Cache creation helper functions for gem5 tutorials.
These functions create L1, L2, L3, and generic caches.
"""

from m5.objects import Cache

def create_cache(size, assoc, tag_latency=1, data_latency=1, response_latency=1, 
                mshrs=4, tgts_per_mshr=4, writeback_clean=False, parent=None):
    """Create and configure a cache object"""
    cache_params = {
        'size': size,
        'assoc': assoc,
        'tag_latency': tag_latency,
        'data_latency': data_latency,
        'response_latency': response_latency,
        'mshrs': mshrs,
        'tgts_per_mshr': tgts_per_mshr,
        'writeback_clean': writeback_clean
    }
    
    # Add parent if provided
    if parent:
        cache_params['parent'] = parent
    
    return Cache(**cache_params)

def create_l1_cache(size="32kB", assoc=8, parent=None):
    """Create an L1 cache with typical parameters"""
    return create_cache(
        size=size, 
        assoc=assoc, 
        tag_latency=1, 
        data_latency=1, 
        response_latency=1, 
        mshrs=16, 
        tgts_per_mshr=12,
        parent=parent
    )

def create_l2_cache(size="256kB", assoc=8, parent=None):
    """Create an L2 cache with typical parameters"""
    return create_cache(
        size=size, 
        assoc=assoc, 
        tag_latency=10, 
        data_latency=10, 
        response_latency=10, 
        mshrs=20, 
        tgts_per_mshr=12,
        parent=parent
    )

def create_l3_cache(size="2MiB", assoc=16, parent=None):
    """Create an L3 cache with typical parameters"""
    return create_cache(
        size=size, 
        assoc=assoc, 
        tag_latency=40, 
        data_latency=40, 
        response_latency=40, 
        mshrs=32, 
        tgts_per_mshr=16,
        parent=parent
    )

# Config dictionary functions
def create_l1_cache_config(size="32kB", assoc=8):
    """Create an L1 cache configuration dictionary"""
    return {
        'size': size,
        'assoc': assoc,
        'tag_latency': 1,
        'data_latency': 1,
        'response_latency': 1,
        'mshrs': 16,
        'tgts_per_mshr': 12
    }

def create_l2_cache_config(size="256kB", assoc=8):
    """Create an L2 cache configuration dictionary"""
    return {
        'size': size,
        'assoc': assoc,
        'tag_latency': 10,
        'data_latency': 10,
        'response_latency': 10,
        'mshrs': 20,
        'tgts_per_mshr': 12
    }

def create_l3_cache_config(size="2MiB", assoc=16):
    """Create an L3 cache configuration dictionary"""
    return {
        'size': size,
        'assoc': assoc,
        'tag_latency': 40,
        'data_latency': 40,
        'response_latency': 40,
        'mshrs': 32,
        'tgts_per_mshr': 16
    }
