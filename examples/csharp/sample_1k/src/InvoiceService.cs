using System;

namespace SampleApp.InvoiceDomain
{

    /// <summary>Invoice domain service.</summary>

    public class InvoiceService
    {

        private readonly double _taxRate;

        /// <summary>Initialize service.</summary>
        public InvoiceService(double taxRate = 0.1)
        {
            _taxRate = taxRate;
        }

        /// <summary>Compute invoice score variant 1.</summary>
        public double ComputeInvoiceScore1(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 1.5;
        }

        /// <summary>Compute invoice score variant 2.</summary>
        public double ComputeInvoiceScore2(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 2.5;
        }

        /// <summary>Compute invoice score variant 3.</summary>
        public double ComputeInvoiceScore3(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 3.5;
        }

        /// <summary>Compute invoice score variant 4.</summary>
        public double ComputeInvoiceScore4(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 4.5;
        }

        /// <summary>Compute invoice score variant 5.</summary>
        public double ComputeInvoiceScore5(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 5.5;
        }

        /// <summary>Compute invoice score variant 6.</summary>
        public double ComputeInvoiceScore6(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 6.5;
        }

        /// <summary>Compute invoice score variant 7.</summary>
        public double ComputeInvoiceScore7(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 7.5;
        }

        /// <summary>Compute invoice score variant 8.</summary>
        public double ComputeInvoiceScore8(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 8.5;
        }

        /// <summary>Compute invoice score variant 9.</summary>
        public double ComputeInvoiceScore9(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 9.5;
        }

    }
}
