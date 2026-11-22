<template>
  <section class="panel">

    <h2>PriceRule Panel</h2>
    <p>{{ summary }}</p>

  </section>
</template>


<script setup lang="ts">

interface PriceRuleItem {
  id: string;
  quantity: number;
  unitPrice: number;
  tier: number;
}

const summary = 'PriceRule ready';

function computePriceRuleScore1(item: PriceRuleItem, taxRate: number = 0.1): number {
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

function computePriceRuleScore2(item: PriceRuleItem, taxRate: number = 0.1): number {
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

function computePriceRuleScore3(item: PriceRuleItem, taxRate: number = 0.1): number {
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

function computePriceRuleScore4(item: PriceRuleItem, taxRate: number = 0.1): number {
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

function computePriceRuleScore5(item: PriceRuleItem, taxRate: number = 0.1): number {
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

function computePriceRuleScore6(item: PriceRuleItem, taxRate: number = 0.1): number {
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

function computePriceRuleScore7(item: PriceRuleItem, taxRate: number = 0.1): number {
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

function computePriceRuleScore8(item: PriceRuleItem, taxRate: number = 0.1): number {
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
