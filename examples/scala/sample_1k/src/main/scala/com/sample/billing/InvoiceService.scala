package com.sample.billing

/** Invoice domain service. */

class InvoiceService(taxRate: Double = 0.1) {

  /** Compute invoice score variant 1. */
  def computeInvoiceScore1(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 1.5
    }
  }

  /** Compute invoice score variant 2. */
  def computeInvoiceScore2(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 2.5
    }
  }

  /** Compute invoice score variant 3. */
  def computeInvoiceScore3(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 3.5
    }
  }

  /** Compute invoice score variant 4. */
  def computeInvoiceScore4(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 4.5
    }
  }

  /** Compute invoice score variant 5. */
  def computeInvoiceScore5(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 5.5
    }
  }

  /** Compute invoice score variant 6. */
  def computeInvoiceScore6(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 6.5
    }
  }

  /** Compute invoice score variant 7. */
  def computeInvoiceScore7(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 7.5
    }
  }

  /** Compute invoice score variant 8. */
  def computeInvoiceScore8(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 8.5
    }
  }

  /** Compute invoice score variant 9. */
  def computeInvoiceScore9(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 9.5
    }
  }

}
