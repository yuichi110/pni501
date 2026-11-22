package com.sample.analytics

/** Metric domain service. */

class MetricService(taxRate: Double = 0.1) {

  /** Compute metric score variant 1. */
  def computeMetricScore1(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 1.5
    }
  }

  /** Compute metric score variant 2. */
  def computeMetricScore2(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 2.5
    }
  }

  /** Compute metric score variant 3. */
  def computeMetricScore3(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 3.5
    }
  }

  /** Compute metric score variant 4. */
  def computeMetricScore4(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 4.5
    }
  }

  /** Compute metric score variant 5. */
  def computeMetricScore5(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 5.5
    }
  }

  /** Compute metric score variant 6. */
  def computeMetricScore6(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 6.5
    }
  }

  /** Compute metric score variant 7. */
  def computeMetricScore7(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 7.5
    }
  }

  /** Compute metric score variant 8. */
  def computeMetricScore8(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 8.5
    }
  }

  /** Compute metric score variant 9. */
  def computeMetricScore9(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 9.5
    }
  }

}
