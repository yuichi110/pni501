import XCTest
@testable import SampleSwift

final class OrderServiceTests: XCTestCase {
    func testOrderScore() {
        let svc = OrderService(taxRate: 0.1)
        XCTAssertGreaterThan(svc.computeOrderScore1(quantity: 2, unitPrice: 10.0, tier: 2), 0.0)
    }

    func testZeroQuantityScore() {
        let svc = OrderService(taxRate: 0.1)
        XCTAssertEqual(svc.computeOrderScore1(quantity: 0, unitPrice: 10.0, tier: 1), 0.0)
    }
}
