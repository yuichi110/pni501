import '../lib/orders.dart';

void testOrderScore() {
  final svc = OrderService();
  assert(svc.computeOrderScore1(2, 10.0, 2) > 0);
  assert(svc.computeOrderScore1(0, 10.0, 1) == 0.0);
}

void main() {
  testOrderScore();
}
