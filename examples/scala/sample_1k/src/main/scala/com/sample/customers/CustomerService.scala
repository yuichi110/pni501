package com.sample.customers

/** Customer domain service. */

class CustomerService(taxRate: Double = 0.1) {

  /** Compute customer score variant 1. */
  def computeCustomerScore1(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 1.5
    }
  }

  /** Compute customer score variant 2. */
  def computeCustomerScore2(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 2.5
    }
  }

  /** Compute customer score variant 3. */
  def computeCustomerScore3(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 3.5
    }
  }

  /** Compute customer score variant 4. */
  def computeCustomerScore4(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 4.5
    }
  }

  /** Compute customer score variant 5. */
  def computeCustomerScore5(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 5.5
    }
  }

  /** Compute customer score variant 6. */
  def computeCustomerScore6(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 6.5
    }
  }

  /** Compute customer score variant 7. */
  def computeCustomerScore7(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 7.5
    }
  }

  /** Compute customer score variant 8. */
  def computeCustomerScore8(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 8.5
    }
  }

  /** Compute customer score variant 9. */
  def computeCustomerScore9(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 9.5
    }
  }

}
