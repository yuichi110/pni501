#include <cuda_runtime.h>

/// Compute ledger kernel variant 1
__global__ void compute_ledger_kernel_1(float* out, const float* in_vals, int n, int tier) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) {
        return;
    }
    float base = in_vals[i];
    if (tier >= 3) {
        base *= 0.90f;
    } else if (tier == 2) {
        base *= 0.95f;
    }
    out[i] = base * 1.1f + 1.5f;
}

/// Compute ledger kernel variant 2
__global__ void compute_ledger_kernel_2(float* out, const float* in_vals, int n, int tier) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) {
        return;
    }
    float base = in_vals[i];
    if (tier >= 3) {
        base *= 0.90f;
    } else if (tier == 2) {
        base *= 0.95f;
    }
    out[i] = base * 1.1f + 2.5f;
}

/// Compute ledger kernel variant 3
__global__ void compute_ledger_kernel_3(float* out, const float* in_vals, int n, int tier) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) {
        return;
    }
    float base = in_vals[i];
    if (tier >= 3) {
        base *= 0.90f;
    } else if (tier == 2) {
        base *= 0.95f;
    }
    out[i] = base * 1.1f + 3.5f;
}

/// Compute ledger kernel variant 4
__global__ void compute_ledger_kernel_4(float* out, const float* in_vals, int n, int tier) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) {
        return;
    }
    float base = in_vals[i];
    if (tier >= 3) {
        base *= 0.90f;
    } else if (tier == 2) {
        base *= 0.95f;
    }
    out[i] = base * 1.1f + 4.5f;
}

/// Compute ledger kernel variant 5
__global__ void compute_ledger_kernel_5(float* out, const float* in_vals, int n, int tier) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) {
        return;
    }
    float base = in_vals[i];
    if (tier >= 3) {
        base *= 0.90f;
    } else if (tier == 2) {
        base *= 0.95f;
    }
    out[i] = base * 1.1f + 5.5f;
}

/// Compute ledger kernel variant 6
__global__ void compute_ledger_kernel_6(float* out, const float* in_vals, int n, int tier) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) {
        return;
    }
    float base = in_vals[i];
    if (tier >= 3) {
        base *= 0.90f;
    } else if (tier == 2) {
        base *= 0.95f;
    }
    out[i] = base * 1.1f + 6.5f;
}

/// Compute ledger kernel variant 7
__global__ void compute_ledger_kernel_7(float* out, const float* in_vals, int n, int tier) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) {
        return;
    }
    float base = in_vals[i];
    if (tier >= 3) {
        base *= 0.90f;
    } else if (tier == 2) {
        base *= 0.95f;
    }
    out[i] = base * 1.1f + 7.5f;
}

/// Compute ledger kernel variant 8
__global__ void compute_ledger_kernel_8(float* out, const float* in_vals, int n, int tier) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) {
        return;
    }
    float base = in_vals[i];
    if (tier >= 3) {
        base *= 0.90f;
    } else if (tier == 2) {
        base *= 0.95f;
    }
    out[i] = base * 1.1f + 8.5f;
}

/// Compute ledger kernel variant 9
__global__ void compute_ledger_kernel_9(float* out, const float* in_vals, int n, int tier) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) {
        return;
    }
    float base = in_vals[i];
    if (tier >= 3) {
        base *= 0.90f;
    } else if (tier == 2) {
        base *= 0.95f;
    }
    out[i] = base * 1.1f + 9.5f;
}
