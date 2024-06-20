NF > 0 && ($2 ~ /^[0-9a-f]/) {
  printf $5 $4 $3 $2 " "
  if ($NF ~ /</) {
    for (i=6; i<NF-1; i++) {
      printf $i " "
    }
    instr_addr = strtonum("0x" substr($1, 1, length($1) - 1))
    printf strtonum($(NF-1)) - instr_addr
  } else {
    for (i=6; i<=NF; i++) {
      # filter our llvm-objdump rounding mode info
      # if (i==(NF-1) && $NF ~ /(dyn|rtz|rmm|rup|rdn|rne)/) {
      #   printf substr($i, 0, length($i) - 1)
      #   break;
      # } else {
        printf $i " "
      # }
    }

  }
  print ""
}
