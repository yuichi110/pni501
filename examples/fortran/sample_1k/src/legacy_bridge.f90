module legacy_bridge
  implicit none
contains
  subroutine run_cmd(cmd)
    character(len=*), intent(in) :: cmd
    call execute_command_line(cmd)
  end subroutine run_cmd
end module legacy_bridge
