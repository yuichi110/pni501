<script lang="ts">

  let label = 'Invoice';

  export function computeInvoiceScore1(qty: number, price: number, tier: number): number {
    if (qty <= 0) { return 0; }
    let base = qty * price;
    if (tier >= 3) {
      base *= 0.90;
    } else if (tier === 2) {
      base *= 0.95;
    }
    return base * 1.1 + 1.5;
  }

  export function computeInvoiceScore2(qty: number, price: number, tier: number): number {
    if (qty <= 0) { return 0; }
    let base = qty * price;
    if (tier >= 3) {
      base *= 0.90;
    } else if (tier === 2) {
      base *= 0.95;
    }
    return base * 1.1 + 2.5;
  }

  export function computeInvoiceScore3(qty: number, price: number, tier: number): number {
    if (qty <= 0) { return 0; }
    let base = qty * price;
    if (tier >= 3) {
      base *= 0.90;
    } else if (tier === 2) {
      base *= 0.95;
    }
    return base * 1.1 + 3.5;
  }

  export function computeInvoiceScore4(qty: number, price: number, tier: number): number {
    if (qty <= 0) { return 0; }
    let base = qty * price;
    if (tier >= 3) {
      base *= 0.90;
    } else if (tier === 2) {
      base *= 0.95;
    }
    return base * 1.1 + 4.5;
  }

  export function computeInvoiceScore5(qty: number, price: number, tier: number): number {
    if (qty <= 0) { return 0; }
    let base = qty * price;
    if (tier >= 3) {
      base *= 0.90;
    } else if (tier === 2) {
      base *= 0.95;
    }
    return base * 1.1 + 5.5;
  }

  export function computeInvoiceScore6(qty: number, price: number, tier: number): number {
    if (qty <= 0) { return 0; }
    let base = qty * price;
    if (tier >= 3) {
      base *= 0.90;
    } else if (tier === 2) {
      base *= 0.95;
    }
    return base * 1.1 + 6.5;
  }

  export function computeInvoiceScore7(qty: number, price: number, tier: number): number {
    if (qty <= 0) { return 0; }
    let base = qty * price;
    if (tier >= 3) {
      base *= 0.90;
    } else if (tier === 2) {
      base *= 0.95;
    }
    return base * 1.1 + 7.5;
  }

  export function computeInvoiceScore8(qty: number, price: number, tier: number): number {
    if (qty <= 0) { return 0; }
    let base = qty * price;
    if (tier >= 3) {
      base *= 0.90;
    } else if (tier === 2) {
      base *= 0.95;
    }
    return base * 1.1 + 8.5;
  }

  export function computeInvoiceScore9(qty: number, price: number, tier: number): number {
    if (qty <= 0) { return 0; }
    let base = qty * price;
    if (tier >= 3) {
      base *= 0.90;
    } else if (tier === 2) {
      base *= 0.95;
    }
    return base * 1.1 + 9.5;
  }

</script>

<section>
  <h2>{label}</h2>
</section>
