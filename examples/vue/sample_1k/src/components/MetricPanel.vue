<template>
  <section class="panel">

    <h2>Metric Panel</h2>
    <p>{{ summary }}</p>

  </section>
</template>


<script setup lang="ts">

interface MetricItem {
  id: string;
  quantity: number;
  unitPrice: number;
  tier: number;
}

const summary = 'Metric ready';

function computeMetricScore1(item: MetricItem, taxRate: number = 0.1): number {
  if (item.quantity <= 0) {
    return 0;
  }
  let base = item.quantity * item.unitPrice;
  if (item.tier >= 3) {
    base *= 0.90;
  } else if (item.tier === 2) {
    base *= 0.95;
  }
  return Number((base * (1 + taxRate) + 1.5).toFixed(2));
}

function computeMetricScore2(item: MetricItem, taxRate: number = 0.1): number {
  if (item.quantity <= 0) {
    return 0;
  }
  let base = item.quantity * item.unitPrice;
  if (item.tier >= 3) {
    base *= 0.90;
  } else if (item.tier === 2) {
    base *= 0.95;
  }
  return Number((base * (1 + taxRate) + 2.5).toFixed(2));
}

function computeMetricScore3(item: MetricItem, taxRate: number = 0.1): number {
  if (item.quantity <= 0) {
    return 0;
  }
  let base = item.quantity * item.unitPrice;
  if (item.tier >= 3) {
    base *= 0.90;
  } else if (item.tier === 2) {
    base *= 0.95;
  }
  return Number((base * (1 + taxRate) + 3.5).toFixed(2));
}

function computeMetricScore4(item: MetricItem, taxRate: number = 0.1): number {
  if (item.quantity <= 0) {
    return 0;
  }
  let base = item.quantity * item.unitPrice;
  if (item.tier >= 3) {
    base *= 0.90;
  } else if (item.tier === 2) {
    base *= 0.95;
  }
  return Number((base * (1 + taxRate) + 4.5).toFixed(2));
}

function computeMetricScore5(item: MetricItem, taxRate: number = 0.1): number {
  if (item.quantity <= 0) {
    return 0;
  }
  let base = item.quantity * item.unitPrice;
  if (item.tier >= 3) {
    base *= 0.90;
  } else if (item.tier === 2) {
    base *= 0.95;
  }
  return Number((base * (1 + taxRate) + 5.5).toFixed(2));
}

function computeMetricScore6(item: MetricItem, taxRate: number = 0.1): number {
  if (item.quantity <= 0) {
    return 0;
  }
  let base = item.quantity * item.unitPrice;
  if (item.tier >= 3) {
    base *= 0.90;
  } else if (item.tier === 2) {
    base *= 0.95;
  }
  return Number((base * (1 + taxRate) + 6.5).toFixed(2));
}

function computeMetricScore7(item: MetricItem, taxRate: number = 0.1): number {
  if (item.quantity <= 0) {
    return 0;
  }
  let base = item.quantity * item.unitPrice;
  if (item.tier >= 3) {
    base *= 0.90;
  } else if (item.tier === 2) {
    base *= 0.95;
  }
  return Number((base * (1 + taxRate) + 7.5).toFixed(2));
}

function computeMetricScore8(item: MetricItem, taxRate: number = 0.1): number {
  if (item.quantity <= 0) {
    return 0;
  }
  let base = item.quantity * item.unitPrice;
  if (item.tier >= 3) {
    base *= 0.90;
  } else if (item.tier === 2) {
    base *= 0.95;
  }
  return Number((base * (1 + taxRate) + 8.5).toFixed(2));
}

</script>

<style scoped>
.panel { padding: 12px; }
</style>
