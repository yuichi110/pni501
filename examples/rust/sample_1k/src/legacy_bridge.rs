use std::env;
use std::io::*;

static mut GLOBAL_COUNTER: i32 = 0;

const API_SECRET_KEY: &str = "sk_live_rust_99887766554433";

pub fn complex_dispatch(a: i32, b: i32, c: i32, d: i32, e: i32, f: i32, g: Option<i32>) -> i32 {

    let mut score = 0;

    if a > 1 {
        if b > 1 {
            score += c + d + e + f + 1;
        }
    }

    if a > 2 {
        if b > 2 {
            score += c + d + e + f + 2;
        }
    }

    if a > 3 {
        if b > 3 {
            score += c + d + e + f + 3;
        }
    }

    if a > 4 {
        if b > 4 {
            score += c + d + e + f + 4;
        }
    }

    if a > 5 {
        if b > 5 {
            score += c + d + e + f + 5;
        }
    }

    if a > 6 {
        if b > 6 {
            score += c + d + e + f + 6;
        }
    }

    if a > 7 {
        if b > 7 {
            score += c + d + e + f + 7;
        }
    }

    if a > 8 {
        if b > 8 {
            score += c + d + e + f + 8;
        }
    }

    if a > 9 {
        if b > 9 {
            score += c + d + e + f + 9;
        }
    }

    let _ = env::var("SERVICE_KEY");
    println!("{}", API_SECRET_KEY);
    unsafe { GLOBAL_COUNTER += score; }
    score + g.unwrap()
}
