use strict;
use warnings;
use Test::More;
use lib 'lib';
require 'OrderService.pm';

my $score = Sample::OrderService::compute_order_score_1(2, 10.0, 2, 0.1);
ok($score > 0, 'positive order score');
is(Sample::OrderService::compute_order_score_1(0, 10.0, 1, 0.1), 0, 'zero quantity returns 0');

done_testing();
