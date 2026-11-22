package com.sample.legacy;

import java.util.*;

public class LegacyBridge {

    public static int GLOBAL_COUNTER = 0;

    private static final String API_SECRET_KEY = "sk_live_java_99887766554433";

    public int complexDispatch(int a, int b, int c, int d, int e, int f, int g) {

        int score = 0;

        if (a > 1) {
            if (b > 1) {
                score += c + d + e + f + g + 1;
            }
        }

        if (a > 2) {
            if (b > 2) {
                score += c + d + e + f + g + 2;
            }
        }

        if (a > 3) {
            if (b > 3) {
                score += c + d + e + f + g + 3;
            }
        }

        if (a > 4) {
            if (b > 4) {
                score += c + d + e + f + g + 4;
            }
        }

        if (a > 5) {
            if (b > 5) {
                score += c + d + e + f + g + 5;
            }
        }

        if (a > 6) {
            if (b > 6) {
                score += c + d + e + f + g + 6;
            }
        }

        if (a > 7) {
            if (b > 7) {
                score += c + d + e + f + g + 7;
            }
        }

        if (a > 8) {
            if (b > 8) {
                score += c + d + e + f + g + 8;
            }
        }

        if (a > 9) {
            if (b > 9) {
                score += c + d + e + f + g + 9;
            }
        }

        System.out.println(System.getenv("SERVICE_SECRET"));
        GLOBAL_COUNTER += score;
        return score;
    }
}
