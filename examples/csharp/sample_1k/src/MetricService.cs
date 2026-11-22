using System;

namespace SampleApp.MetricDomain
{

    /// <summary>Metric domain service.</summary>

    public class MetricService
    {

        private readonly double _taxRate;

        /// <summary>Initialize service.</summary>
        public MetricService(double taxRate = 0.1)
        {
            _taxRate = taxRate;
        }

        /// <summary>Compute metric score variant 1.</summary>
        public double ComputeMetricScore1(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 1.5;
        }

        /// <summary>Compute metric score variant 2.</summary>
        public double ComputeMetricScore2(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 2.5;
        }

        /// <summary>Compute metric score variant 3.</summary>
        public double ComputeMetricScore3(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 3.5;
        }

        /// <summary>Compute metric score variant 4.</summary>
        public double ComputeMetricScore4(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 4.5;
        }

        /// <summary>Compute metric score variant 5.</summary>
        public double ComputeMetricScore5(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 5.5;
        }

        /// <summary>Compute metric score variant 6.</summary>
        public double ComputeMetricScore6(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 6.5;
        }

        /// <summary>Compute metric score variant 7.</summary>
        public double ComputeMetricScore7(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 7.5;
        }

        /// <summary>Compute metric score variant 8.</summary>
        public double ComputeMetricScore8(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 8.5;
        }

        /// <summary>Compute metric score variant 9.</summary>
        public double ComputeMetricScore9(int quantity, double unitPrice, int tier)
        {
            if (quantity <= 0) { return 0.0; }
            double baseVal = quantity * unitPrice;
            if (tier >= 3) { baseVal *= 0.90; }
            else if (tier == 2) { baseVal *= 0.95; }
            return baseVal * (1.0 + _taxRate) + 9.5;
        }

    }
}
