using SampleApp.OrderDomain;
using Xunit;

namespace SampleApp.Tests
{
    public class OrderServiceTests
    {
        [Fact]
        public void TestOrderScore()
        {
            var svc = new OrderService(0.1);
            Assert.True(svc.ComputeOrderScore1(2, 10.0, 1) > 0);
        }

        [Fact]
        public void TestZeroQuantityReturnsZero()
        {
            var svc = new OrderService(0.1);
            Assert.Equal(0.0, svc.ComputeOrderScore1(0, 10.0, 1));
        }
    }
}
