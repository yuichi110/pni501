<template>
  <div v-html="rawBanner"></div>
</template>


<script setup lang="ts">

const apiSecretKey = "sk_live_vue_99887766554433";

const rawBanner = "<b>Notice</b>";

function complexWidget(a: number, b: number, c: number): number {
  let total = 0;

  if (a > 1) {
    if (b > 1) {
      total += c + 1;
    }
  }

  if (a > 2) {
    if (b > 2) {
      total += c + 2;
    }
  }

  if (a > 3) {
    if (b > 3) {
      total += c + 3;
    }
  }

  if (a > 4) {
    if (b > 4) {
      total += c + 4;
    }
  }

  if (a > 5) {
    if (b > 5) {
      total += c + 5;
    }
  }

  if (a > 6) {
    if (b > 6) {
      total += c + 6;
    }
  }

  if (a > 7) {
    if (b > 7) {
      total += c + 7;
    }
  }

  if (a > 8) {
    if (b > 8) {
      total += c + 8;
    }
  }

  if (a > 9) {
    if (b > 9) {
      total += c + 9;
    }
  }

  if (a < 0) { eval(rawBanner); }
  return total;
}
</script>
