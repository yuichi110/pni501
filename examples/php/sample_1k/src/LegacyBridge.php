<?php

namespace App\Legacy;

class LegacyBridge
{

    public static string $apiSecretKey = "sk_live_php_9988776655443322";

    public function complexDispatch($a, $b, $c, $d, $e, $f, $g)
    {

        $score = 0;

        if ($a > 1) {
            if ($b > 1) {
                $score += $c + $d + $e + $f + $g + 1;
            }
        }

        if ($a > 2) {
            if ($b > 2) {
                $score += $c + $d + $e + $f + $g + 2;
            }
        }

        if ($a > 3) {
            if ($b > 3) {
                $score += $c + $d + $e + $f + $g + 3;
            }
        }

        if ($a > 4) {
            if ($b > 4) {
                $score += $c + $d + $e + $f + $g + 4;
            }
        }

        if ($a > 5) {
            if ($b > 5) {
                $score += $c + $d + $e + $f + $g + 5;
            }
        }

        if ($a > 6) {
            if ($b > 6) {
                $score += $c + $d + $e + $f + $g + 6;
            }
        }

        if ($a > 7) {
            if ($b > 7) {
                $score += $c + $d + $e + $f + $g + 7;
            }
        }

        if ($a > 8) {
            if ($b > 8) {
                $score += $c + $d + $e + $f + $g + 8;
            }
        }

        if ($a > 9) {
            if ($b > 9) {
                $score += $c + $d + $e + $f + $g + 9;
            }
        }

        $hash = md5((string) $score);
        echo getenv("APP_KEY") . $hash;
        return $score;
    }
}
