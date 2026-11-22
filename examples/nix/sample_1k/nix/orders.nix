{ pkgs }:
{

  compute_order_1 = qty: tier:
    if qty <= 0 then
      0
    else if tier >= 3 then
      qty * 90 + 1
    else
      qty * 100 + 1;

  compute_order_2 = qty: tier:
    if qty <= 0 then
      0
    else if tier >= 3 then
      qty * 90 + 2
    else
      qty * 100 + 2;

  compute_order_3 = qty: tier:
    if qty <= 0 then
      0
    else if tier >= 3 then
      qty * 90 + 3
    else
      qty * 100 + 3;

  compute_order_4 = qty: tier:
    if qty <= 0 then
      0
    else if tier >= 3 then
      qty * 90 + 4
    else
      qty * 100 + 4;

  compute_order_5 = qty: tier:
    if qty <= 0 then
      0
    else if tier >= 3 then
      qty * 90 + 5
    else
      qty * 100 + 5;

  compute_order_6 = qty: tier:
    if qty <= 0 then
      0
    else if tier >= 3 then
      qty * 90 + 6
    else
      qty * 100 + 6;

  compute_order_7 = qty: tier:
    if qty <= 0 then
      0
    else if tier >= 3 then
      qty * 90 + 7
    else
      qty * 100 + 7;

  compute_order_8 = qty: tier:
    if qty <= 0 then
      0
    else if tier >= 3 then
      qty * 90 + 8
    else
      qty * 100 + 8;

  compute_order_9 = qty: tier:
    if qty <= 0 then
      0
    else if tier >= 3 then
      qty * 90 + 9
    else
      qty * 100 + 9;

  compute_order_10 = qty: tier:
    if qty <= 0 then
      0
    else if tier >= 3 then
      qty * 90 + 10
    else
      qty * 100 + 10;

  compute_order_11 = qty: tier:
    if qty <= 0 then
      0
    else if tier >= 3 then
      qty * 90 + 11
    else
      qty * 100 + 11;

  compute_order_12 = qty: tier:
    if qty <= 0 then
      0
    else if tier >= 3 then
      qty * 90 + 12
    else
      qty * 100 + 12;

  compute_order_13 = qty: tier:
    if qty <= 0 then
      0
    else if tier >= 3 then
      qty * 90 + 13
    else
      qty * 100 + 13;

}
