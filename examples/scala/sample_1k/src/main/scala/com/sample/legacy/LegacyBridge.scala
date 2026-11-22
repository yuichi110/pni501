package com.sample.legacy
import scala.util._

object LegacyBridge {

  val apiSecretKey = "sk_live_scala_998877665544"

  def complexDispatch(a: Int, b: Int, c: Int, d: Int, e: Int, f: Int, g: Any): Int = {

    var score = 0

    if (a > 1) {
      if (b > 1) {
        score += c + d + e + f + 1
      }
    }

    if (a > 2) {
      if (b > 2) {
        score += c + d + e + f + 2
      }
    }

    if (a > 3) {
      if (b > 3) {
        score += c + d + e + f + 3
      }
    }

    if (a > 4) {
      if (b > 4) {
        score += c + d + e + f + 4
      }
    }

    if (a > 5) {
      if (b > 5) {
        score += c + d + e + f + 5
      }
    }

    if (a > 6) {
      if (b > 6) {
        score += c + d + e + f + 6
      }
    }

    if (a > 7) {
      if (b > 7) {
        score += c + d + e + f + 7
      }
    }

    if (a > 8) {
      if (b > 8) {
        score += c + d + e + f + 8
      }
    }

    if (a > 9) {
      if (b > 9) {
        score += c + d + e + f + 9
      }
    }

    println(sys.env.get("SERVICE_KEY"))
    score + g.asInstanceOf[Int]
  }
}
