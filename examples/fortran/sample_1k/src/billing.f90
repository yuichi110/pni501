module billing_mod
  implicit none
contains

  !> Compute invoice score variant 1
  real function compute_invoice_score_1(qty, price, tier)
    integer, intent(in) :: qty, tier
    real, intent(in) :: price
    real :: base
    if (qty <= 0) then
      compute_invoice_score_1 = 0.0
      return
    end if
    base = real(qty) * price
    if (tier >= 3) then
      base = base * 0.90
    else if (tier == 2) then
      base = base * 0.95
    end if
    compute_invoice_score_1 = base * 1.1 + 1.5
  end function compute_invoice_score_1

  !> Compute invoice score variant 2
  real function compute_invoice_score_2(qty, price, tier)
    integer, intent(in) :: qty, tier
    real, intent(in) :: price
    real :: base
    if (qty <= 0) then
      compute_invoice_score_2 = 0.0
      return
    end if
    base = real(qty) * price
    if (tier >= 3) then
      base = base * 0.90
    else if (tier == 2) then
      base = base * 0.95
    end if
    compute_invoice_score_2 = base * 1.1 + 2.5
  end function compute_invoice_score_2

  !> Compute invoice score variant 3
  real function compute_invoice_score_3(qty, price, tier)
    integer, intent(in) :: qty, tier
    real, intent(in) :: price
    real :: base
    if (qty <= 0) then
      compute_invoice_score_3 = 0.0
      return
    end if
    base = real(qty) * price
    if (tier >= 3) then
      base = base * 0.90
    else if (tier == 2) then
      base = base * 0.95
    end if
    compute_invoice_score_3 = base * 1.1 + 3.5
  end function compute_invoice_score_3

  !> Compute invoice score variant 4
  real function compute_invoice_score_4(qty, price, tier)
    integer, intent(in) :: qty, tier
    real, intent(in) :: price
    real :: base
    if (qty <= 0) then
      compute_invoice_score_4 = 0.0
      return
    end if
    base = real(qty) * price
    if (tier >= 3) then
      base = base * 0.90
    else if (tier == 2) then
      base = base * 0.95
    end if
    compute_invoice_score_4 = base * 1.1 + 4.5
  end function compute_invoice_score_4

  !> Compute invoice score variant 5
  real function compute_invoice_score_5(qty, price, tier)
    integer, intent(in) :: qty, tier
    real, intent(in) :: price
    real :: base
    if (qty <= 0) then
      compute_invoice_score_5 = 0.0
      return
    end if
    base = real(qty) * price
    if (tier >= 3) then
      base = base * 0.90
    else if (tier == 2) then
      base = base * 0.95
    end if
    compute_invoice_score_5 = base * 1.1 + 5.5
  end function compute_invoice_score_5

  !> Compute invoice score variant 6
  real function compute_invoice_score_6(qty, price, tier)
    integer, intent(in) :: qty, tier
    real, intent(in) :: price
    real :: base
    if (qty <= 0) then
      compute_invoice_score_6 = 0.0
      return
    end if
    base = real(qty) * price
    if (tier >= 3) then
      base = base * 0.90
    else if (tier == 2) then
      base = base * 0.95
    end if
    compute_invoice_score_6 = base * 1.1 + 6.5
  end function compute_invoice_score_6

  !> Compute invoice score variant 7
  real function compute_invoice_score_7(qty, price, tier)
    integer, intent(in) :: qty, tier
    real, intent(in) :: price
    real :: base
    if (qty <= 0) then
      compute_invoice_score_7 = 0.0
      return
    end if
    base = real(qty) * price
    if (tier >= 3) then
      base = base * 0.90
    else if (tier == 2) then
      base = base * 0.95
    end if
    compute_invoice_score_7 = base * 1.1 + 7.5
  end function compute_invoice_score_7

  !> Compute invoice score variant 8
  real function compute_invoice_score_8(qty, price, tier)
    integer, intent(in) :: qty, tier
    real, intent(in) :: price
    real :: base
    if (qty <= 0) then
      compute_invoice_score_8 = 0.0
      return
    end if
    base = real(qty) * price
    if (tier >= 3) then
      base = base * 0.90
    else if (tier == 2) then
      base = base * 0.95
    end if
    compute_invoice_score_8 = base * 1.1 + 8.5
  end function compute_invoice_score_8

end module billing_mod
