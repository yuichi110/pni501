using System;

namespace SampleApp.LedgerEntryDomain
{

    /// <summary>LedgerEntry domain service.</summary>

    public class LedgerEntryService
    {

        private readonly double _taxRate;

        /// <summary>Initialize service.</summary>
        public LedgerEntryService(double taxRate = 0.1)
        {
            _taxRate = taxRate;
        }

        /// <summary>Compute ledger score variant 1.</summary>
        public double ComputeLedgerEntryScore1(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 1.5;
        }

        /// <summary>Compute ledger score variant 2.</summary>
        public double ComputeLedgerEntryScore2(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 2.5;
        }

        /// <summary>Compute ledger score variant 3.</summary>
        public double ComputeLedgerEntryScore3(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 3.5;
        }

        /// <summary>Compute ledger score variant 4.</summary>
        public double ComputeLedgerEntryScore4(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 4.5;
        }

        /// <summary>Compute ledger score variant 5.</summary>
        public double ComputeLedgerEntryScore5(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 5.5;
        }

        /// <summary>Compute ledger score variant 6.</summary>
        public double ComputeLedgerEntryScore6(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 6.5;
        }

        /// <summary>Compute ledger score variant 7.</summary>
        public double ComputeLedgerEntryScore7(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 7.5;
        }

        /// <summary>Compute ledger score variant 8.</summary>
        public double ComputeLedgerEntryScore8(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 8.5;
        }

        /// <summary>Compute ledger score variant 9.</summary>
        public double ComputeLedgerEntryScore9(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 9.5;
        }

    }
}
