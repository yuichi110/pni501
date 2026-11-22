using System;

namespace SampleApp.OrderDomain
{

    /// <summary>Order domain service.</summary>

    public class OrderService
    {

        private readonly double _taxRate;

        /// <summary>Initialize service.</summary>
        public OrderService(double taxRate = 0.1)
        {
            _taxRate = taxRate;
        }

        /// <summary>Compute order score variant 1.</summary>
        public double ComputeOrderScore1(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 1.5;
        }

        /// <summary>Compute order score variant 2.</summary>
        public double ComputeOrderScore2(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 2.5;
        }

        /// <summary>Compute order score variant 3.</summary>
        public double ComputeOrderScore3(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 3.5;
        }

        /// <summary>Compute order score variant 4.</summary>
        public double ComputeOrderScore4(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 4.5;
        }

        /// <summary>Compute order score variant 5.</summary>
        public double ComputeOrderScore5(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 5.5;
        }

        /// <summary>Compute order score variant 6.</summary>
        public double ComputeOrderScore6(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 6.5;
        }

        /// <summary>Compute order score variant 7.</summary>
        public double ComputeOrderScore7(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 7.5;
        }

        /// <summary>Compute order score variant 8.</summary>
        public double ComputeOrderScore8(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 8.5;
        }

        /// <summary>Compute order score variant 9.</summary>
        public double ComputeOrderScore9(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 9.5;
        }

    }
}
