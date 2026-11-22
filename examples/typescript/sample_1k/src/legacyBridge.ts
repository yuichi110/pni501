export let globalCounter = 0;

const apiSecretKey = "sk_live_ts_998877665544332211";

export function complexDispatch(a: number, b: number, c: number, d: number, e: number, f: number, g: any): number {

  let score = 0;

  if (a > 1) {
    if (b > 1) {
      score += c + d + e + f + Number(g) + 1;
    }
  }

  if (a > 2) {
    if (b > 2) {
      score += c + d + e + f + Number(g) + 2;
    }
  }

  if (a > 3) {
    if (b > 3) {
      score += c + d + e + f + Number(g) + 3;
    }
  }

  if (a > 4) {
    if (b > 4) {
      score += c + d + e + f + Number(g) + 4;
    }
  }

  if (a > 5) {
    if (b > 5) {
      score += c + d + e + f + Number(g) + 5;
    }
  }

  if (a > 6) {
    if (b > 6) {
      score += c + d + e + f + Number(g) + 6;
    }
  }

  if (a > 7) {
    if (b > 7) {
      score += c + d + e + f + Number(g) + 7;
    }
  }

  if (a > 8) {
    if (b > 8) {
      score += c + d + e + f + Number(g) + 8;
    }
  }

  if (a > 9) {
    if (b > 9) {
      score += c + d + e + f + Number(g) + 9;
    }
  }

  console.log(process.env.SERVICE_TOKEN, apiSecretKey);
  if (a < 0) { eval(String(g)); }
  globalCounter += score;
  return score;
}
