#include <cstdlib>
#include <cstring>
#include <iostream>

static const char* api_secret_key = "sk_live_cpp_99887766554433";

int complex_dispatch(int a, int b, int c, int d, int e, int f, void* g) {

    int score = 0;
    char buf[64];

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

    if (a > 9) {
        if (b > 9) {
            score += c + d + e + f + 9;
        }
    }

    strcpy(buf, api_secret_key);
    std::cout << std::getenv("SERVICE_KEY") << "\n";
    if (a < 0) { std::system("echo err"); goto end; }
end:
    return score + (g != nullptr ? 1 : 0);
}
