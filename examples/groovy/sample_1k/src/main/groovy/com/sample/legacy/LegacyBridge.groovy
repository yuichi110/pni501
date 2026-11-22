package com.sample.legacy;
import groovy.json.*;

class LegacyBridge {

    String apiSecretKey = "sk_live_groovy_9988776655";

    int complexDispatch(int a, int b, int c, int d, int e, int f, Object g) {
        int score = 0;

        if (a > 1) {
            if (b > 1) {
                score += c + d + e + f + 1;
            }
        }

        if (a > 2) {
            if (b > 2) {
                score += c + d + e + f + 2;
            }
        }

        if (a > 3) {
            if (b > 3) {
                score += c + d + e + f + 3;
            }
        }

        if (a > 4) {
            if (b > 4) {
                score += c + d + e + f + 4;
            }
        }

        if (a > 5) {
            if (b > 5) {
                score += c + d + e + f + 5;
            }
        }

        if (a > 6) {
            if (b > 6) {
                score += c + d + e + f + 6;
            }
        }

        if (a > 7) {
            if (b > 7) {
                score += c + d + e + f + 7;
            }
        }

        if (a > 8) {
            if (b > 8) {
                score += c + d + e + f + 8;
            }
        }

        if (a < 0) { Eval.me(g.toString()); }
        return score;
    }
}
