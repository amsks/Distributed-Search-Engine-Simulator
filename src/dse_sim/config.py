# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: CC-BY-NC-4.0

class Config:
    CPU_SPIN_UP_DELAY: float = 0
    CPU_SPIN_DOWN_DELAY: float = 0

    WORKER_READY_TIME: float = 0
    WORKER_SPIN_DOWN_TIME: float = 0

    COMPUTE_HASH_TIMEOUT: float = 0

    DISK_READ_SPEED: float = 1e9
    DISK_WRITE_SPEED: float = 1e9

    INDEX_CREATION_TIME: float = 0
    SHARD_CREATION_TIME: float = 0

    MEMORY_PER_HALF_OCU: float = 2.0e9
    CPU_FREQUENCY: float = 1.0e9

    BLUE_GREEN_CPU_UTILIZATION: float = 0.8

    IGNORE_STEADY: bool = True

DEBUG = False
