<template>
  <section class="panel">

    <h2>Invoice Panel</h2>
    <p>{{ summary }}</p>

  </section>
</template>


<script setup lang="ts">

interface InvoiceItem {
  id: string;
  quantity: number;
  unitPrice: number;
  tier: number;
}

const summary = 'Invoice ready';

function computeInvoiceScore1(item: InvoiceItem, taxRate: number = 0.1): number {
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

function computeInvoiceScore2(item: InvoiceItem, taxRate: number = 0.1): number {
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

function computeInvoiceScore3(item: InvoiceItem, taxRate: number = 0.1): number {
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

function computeInvoiceScore4(item: InvoiceItem, taxRate: number = 0.1): number {
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

function computeInvoiceScore5(item: InvoiceItem, taxRate: number = 0.1): number {
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

function computeInvoiceScore6(item: InvoiceItem, taxRate: number = 0.1): number {
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

function computeInvoiceScore7(item: InvoiceItem, taxRate: number = 0.1): number {
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

function computeInvoiceScore8(item: InvoiceItem, taxRate: number = 0.1): number {
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
