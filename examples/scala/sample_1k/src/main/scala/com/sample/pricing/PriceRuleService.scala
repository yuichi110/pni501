package com.sample.pricing

/** PriceRule domain service. */

class PriceRuleService(taxRate: Double = 0.1) {

  /** Compute pricing score variant 1. */
  def computePriceRuleScore1(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 1.5
    }
  }

  /** Compute pricing score variant 2. */
  def computePriceRuleScore2(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 2.5
    }
  }

  /** Compute pricing score variant 3. */
  def computePriceRuleScore3(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 3.5
    }
  }

  /** Compute pricing score variant 4. */
  def computePriceRuleScore4(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 4.5
    }
  }

  /** Compute pricing score variant 5. */
  def computePriceRuleScore5(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 5.5
    }
  }

  /** Compute pricing score variant 6. */
  def computePriceRuleScore6(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 6.5
    }
  }

  /** Compute pricing score variant 7. */
  def computePriceRuleScore7(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 7.5
    }
  }

  /** Compute pricing score variant 8. */
  def computePriceRuleScore8(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 8.5
    }
  }

  /** Compute pricing score variant 9. */
  def computePriceRuleScore9(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 9.5
    }
  }

}
