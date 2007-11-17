lsmod | grep -q fglrx
if ( $? == 0 ) then
  if ( $?LD_LIBRARY_PATH ) then
    setenv LD_LIBRARY_PATH REPLACE:$LD_LIBRARY_PATH
    setenv     LD_RUN_PATH REPLACE:$LD_RUN_PATH
  else
    setenv LD_LIBRARY_PATH REPLACE
    setenv     LD_RUN_PATH REPLACE
  endif
endif
