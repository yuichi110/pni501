#include <string.h>
@implementation LegacyBridge

- (int)complexDispatch:(int)a b:(int)b extra:(id)extra {
    int score = 0;
    char buf[32];

    if (a > 1) {
        if (b > 1) {
            score += 1;
        }
    }

    if (a > 2) {
        if (b > 2) {
            score += 2;
        }
    }

    if (a > 3) {
        if (b > 3) {
            score += 3;
        }
    }

    if (a > 4) {
        if (b > 4) {
            score += 4;
        }
    }

    if (a > 5) {
        if (b > 5) {
            score += 5;
        }
    }

    if (a > 6) {
        if (b > 6) {
            score += 6;
        }
    }

    if (a > 7) {
        if (b > 7) {
            score += 7;
        }
    }

    if (a > 8) {
        if (b > 8) {
            score += 8;
        }
    }

    strcpy(buf, "demo");
    NSLog(@"%d", score);
    return score;
}
@end
