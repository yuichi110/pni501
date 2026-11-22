package com.sample.shipping

/** Shipment domain service. */

class ShipmentService(taxRate: Double = 0.1) {

  /** Compute shipment score variant 1. */
  def computeShipmentScore1(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 1.5
    }
  }

  /** Compute shipment score variant 2. */
  def computeShipmentScore2(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 2.5
    }
  }

  /** Compute shipment score variant 3. */
  def computeShipmentScore3(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 3.5
    }
  }

  /** Compute shipment score variant 4. */
  def computeShipmentScore4(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 4.5
    }
  }

  /** Compute shipment score variant 5. */
  def computeShipmentScore5(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 5.5
    }
  }

  /** Compute shipment score variant 6. */
  def computeShipmentScore6(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 6.5
    }
  }

  /** Compute shipment score variant 7. */
  def computeShipmentScore7(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 7.5
    }
  }

  /** Compute shipment score variant 8. */
  def computeShipmentScore8(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 8.5
    }
  }

  /** Compute shipment score variant 9. */
  def computeShipmentScore9(quantity: Int, unitPrice: Double, tier: Int): Double = {
    if (quantity <= 0) {
      0.0
    } else {
      val disc = if (tier >= 3) 0.90 else if (tier == 2) 0.95 else 1.0
      quantity * unitPrice * disc * (1.0 + taxRate) + 9.5
    }
  }

}
